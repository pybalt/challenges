import { z } from "zod";
import { type InferSchema } from "xmcp";
import { exec } from "child_process";

// Define the schema for tool parameters
export const schema = {
  format: z.enum(["png", "jpg"]).default("png").describe("Image format"),
  quality: z.number().min(1).max(100).default(90).describe("Image quality (1-100, only for JPG)"),
  region: z.object({
    x: z.number().describe("X coordinate of the region to capture"),
    y: z.number().describe("Y coordinate of the region to capture"),
    width: z.number().describe("Width of the region to capture"),
    height: z.number().describe("Height of the region to capture"),
  }).optional().describe("Optional region to capture. If not provided, captures the full screen"),
  resize: z.object({
    width: z.number(),
    height: z.number(),
  }).optional().describe("Optional resize dimensions"),
};

// Define tool metadata
export const metadata = {
  name: "capture_screen",
  description: "Your eyes - OBSERVATION ONLY, no interaction possible. Use this to see the current state of the screen. Always capture first to understand what you're working with. Essential for monitoring progress. Supports zoom functionality: capture specific regions and resize them for detailed analysis of UI elements. You CANNOT click on anything you see.",
  annotations: {
    title: "Capture Screen",
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
  },
};

// Tool implementation
export default async function captureScreen({ format, quality, region, resize }: InferSchema<typeof schema>) {
  return new Promise((resolve) => {
    try {
      const timestamp = Date.now();
      
      // PowerShell script to capture screen
      let psCommand = `
        Add-Type -AssemblyName System.Windows.Forms;
        Add-Type -AssemblyName System.Drawing;
        
        $screenBounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;
        $screenWidth = $screenBounds.Width;
        $screenHeight = $screenBounds.Height;
        
        Write-Output "Screen resolution: $screenWidth x $screenHeight";
      `;
      
      if (region) {
        // Capture specific region
        psCommand += `
          $captureWidth = ${region.width};
          $captureHeight = ${region.height};
          $captureX = ${region.x};
          $captureY = ${region.y};
          
          Write-Output "Capturing region: $captureX,$captureY ${region.width}x${region.height}";
        `;
      } else {
        // Capture full screen
        psCommand += `
          $captureWidth = $screenWidth;
          $captureHeight = $screenHeight;
          $captureX = 0;
          $captureY = 0;
          
          Write-Output "Capturing full screen: ${0},${0} $screenWidth x $screenHeight";
        `;
      }
      
      psCommand += `
        $bitmap = New-Object System.Drawing.Bitmap($captureWidth, $captureHeight);
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap);
        $graphics.CopyFromScreen($captureX, $captureY, 0, 0, $bitmap.Size);
        $graphics.Dispose();
      `;
      
      if (resize) {
        psCommand += `
          $resizedBitmap = New-Object System.Drawing.Bitmap(${resize.width}, ${resize.height});
          $resizedGraphics = [System.Drawing.Graphics]::FromImage($resizedBitmap);
          $resizedGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;
          $resizedGraphics.DrawImage($bitmap, 0, 0, ${resize.width}, ${resize.height});
          $resizedGraphics.Dispose();
          $bitmap.Dispose();
          $bitmap = $resizedBitmap;
          
          Write-Output "Resized to: ${resize.width}x${resize.height}";
        `;
      }
      
      psCommand += `
        $stream = New-Object System.IO.MemoryStream;
        $bitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::${format.toUpperCase()});
        $bitmap.Dispose();
        $bytes = $stream.ToArray();
        $stream.Dispose();
        $base64 = [System.Convert]::ToBase64String($bytes);
        
        Write-Output "Image captured successfully - $([math]::Round($bytes.Length / 1024))KB ${format.toUpperCase()}";
        Write-Output "BASE64:$base64";
      `;

      exec(`powershell -Command "${psCommand.replace(/\n/g, ' ')}"`, { maxBuffer: 50 * 1024 * 1024 }, (error, stdout, stderr) => {
        if (error) {
          console.error("Screen capture error:", error);
          resolve({
            content: [
              {
                type: "text",
                text: `Error capturing screen: ${error.message}`,
              },
            ],
          });
          return;
        }

        const lines = stdout.trim().split('\n');
        const base64Line = lines.find(line => line.startsWith('BASE64:'));
        
        if (!base64Line) {
          resolve({
            content: [
              {
                type: "text",
                text: "Error: Could not extract base64 image data",
              },
            ],
          });
          return;
        }

        const base64Data = base64Line.substring(7); // Remove 'BASE64:' prefix
        const infoLines = lines.filter(line => !line.startsWith('BASE64:'));
        
        resolve({
          content: [
            {
              type: "image",
              data: base64Data,
              mimeType: `image/${format}`,
            },
            {
              type: "text",
              text: `${infoLines.join('\n')} at ${new Date(timestamp).toLocaleString()}`,
            },
          ],
        });
      });
    } catch (error) {
      resolve({
        content: [
          {
            type: "text",
            text: `Error setting up screen capture: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      });
    }
  });
}
