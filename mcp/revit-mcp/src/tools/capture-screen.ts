import { z } from "zod";
import { type InferSchema } from "xmcp";
import { exec } from "child_process";

// Define the schema for tool parameters
export const schema = {
  region: z.object({
    x: z.number().describe("X coordinate of the region to capture"),
    y: z.number().describe("Y coordinate of the region to capture"),
    width: z.number().describe("Width of the region to capture"),
    height: z.number().describe("Height of the region to capture"),
  }).optional().describe("Optional region to capture. If not provided, captures the full screen"),
  format: z.enum(["png", "jpg"]).default("png").describe("Image format"),
  quality: z.number().min(1).max(100).default(90).describe("Image quality (1-100, only for JPG)"),
  resize: z.object({
    width: z.number().optional(),
    height: z.number().optional(),
  }).optional().describe("Optional resize dimensions"),
};

// Define tool metadata
export const metadata = {
  name: "capture_screen",
  description: "Capture the current screen or a specific region and return as base64 image",
  annotations: {
    title: "Screen Capture",
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: false,
  },
};

// Tool implementation
export default async function captureScreen({ region, format, quality, resize }: InferSchema<typeof schema>) {
  try {
    const timestamp = Date.now();
    
    // Simple PowerShell command
    const psCommand = `powershell -Command "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; $screen = [System.Windows.Forms.Screen]::PrimaryScreen; $bounds = $screen.Bounds; $bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height); $graphics = [System.Drawing.Graphics]::FromImage($bitmap); $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size); $ms = New-Object System.IO.MemoryStream; $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png); $bytes = $ms.ToArray(); $base64 = [Convert]::ToBase64String($bytes); Write-Output $base64; $graphics.Dispose(); $bitmap.Dispose(); $ms.Dispose()"`;
    
    // Execute with increased buffer for high quality
    const base64 = await new Promise<string>((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('PowerShell timeout after 10 seconds'));
      }, 10000);
      
      exec(psCommand, { 
        timeout: 10000,
        maxBuffer: 50 * 1024 * 1024 // 50MB buffer for high quality images
      }, (error, stdout, stderr) => {
        clearTimeout(timeoutId);
        
        if (error) {
          reject(error);
          return;
        }
        
        if (stderr) {
          console.error('PowerShell stderr:', stderr);
        }
        
        const result = stdout.trim();
        if (result && result.length > 100) {
          resolve(result);
        } else {
          reject(new Error('Invalid image data returned'));
        }
      });
    });
    
    return {
      content: [
        {
          type: "image",
          data: base64,
          mimeType: "image/png",
        },
        {
          type: "text",
          text: `Screen captured successfully - ${Math.round(base64.length / 1024)}KB PNG at ${new Date(timestamp).toLocaleString()}`,
        },
      ],
    };
  } catch (error) {
    console.error("Screen capture error:", error);
    return {
      content: [
        {
          type: "text",
          text: `Error capturing screen: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
