import { z } from "zod";
import { type InferSchema } from "xmcp";
import { exec } from "child_process";

// Define the schema for tool parameters
export const schema = {
  keys: z.string().describe("Keys to send. Use + for combinations (e.g., 'ctrl+s'), [key] for special keys (e.g., '[enter]'), or regular text"),
  delay: z.number().min(0).max(5000).default(100).describe("Delay between key presses in milliseconds (default: 100)"),
  simultaneous: z.boolean().default(true).describe("Whether to press key combinations simultaneously (default: true)"),
};

// Define tool metadata
export const metadata = {
  name: "send_keys",
  description: "Send keyboard input to the active window. Supports text, key combinations, and special keys.",
  annotations: {
    title: "Send Keys",
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
  },
};

// Tool implementation
export default async function sendKeys({ keys, delay, simultaneous }: InferSchema<typeof schema>) {
  return new Promise((resolve) => {
    try {
      const timestamp = Date.now();
      
      // Convert keys to SendKeys format
      const sendKeysString = convertToSendKeysFormat(keys);
      
      // Simple PowerShell command to send keys
      const psCommand = `Add-Type -AssemblyName System.Windows.Forms; Start-Sleep -Milliseconds ${delay}; [System.Windows.Forms.SendKeys]::SendWait('${sendKeysString}'); Write-Output "Keys sent successfully"`;

      exec(`powershell -Command "${psCommand}"`, (error, stdout, stderr) => {
        if (error) {
          console.error("Send keys error:", error);
          resolve({
            content: [
              {
                type: "text",
                text: `Error sending keys: ${error.message}. Make sure PowerShell is available and the target window is active.`,
              },
            ],
          });
          return;
        }

        resolve({
          content: [
            {
              type: "text",
              text: `Successfully sent keys: "${keys}" at ${new Date(timestamp).toLocaleString()}. Delay: ${delay}ms`,
            },
          ],
        });
      });
    } catch (error) {
      resolve({
        content: [
          {
            type: "text",
            text: `Error setting up key sending: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      });
    }
  });
}

// Convert our key format to Windows SendKeys format
function convertToSendKeysFormat(keys: string): string {
  // Handle key combinations (e.g., "ctrl+s", "alt+tab")
  if (keys.includes('+')) {
    const parts = keys.toLowerCase().split('+').map(s => s.trim());
    let result = '';
    
    // Build the SendKeys string with modifiers
    for (let i = 0; i < parts.length - 1; i++) {
      const modifier = parts[i];
      switch (modifier) {
        case 'ctrl':
        case 'control':
          result += '^';
          break;
        case 'alt':
          result += '%';
          break;
        case 'shift':
          result += '+';
          break;
        case 'win':
        case 'cmd':
          result += '^{ESC}'; // Windows key approximation
          break;
      }
    }
    
    // Add the main key
    const mainKey = parts[parts.length - 1];
    result += convertSingleKey(mainKey);
    
    return result;
  }
  
  // Handle special keys in brackets (e.g., "[enter]", "[tab]")
  if (keys.match(/\[.*\]/)) {
    return keys.replace(/\[([^\]]+)\]/g, (match, key) => {
      return convertSingleKey(key.toLowerCase());
    });
  }
  
  // Handle regular text - escape special characters
  return keys.replace(/[+^%~(){}]/g, '{$&}');
}

// Convert a single key to SendKeys format
function convertSingleKey(key: string): string {
  const keyMap: Record<string, string> = {
    'enter': '{ENTER}',
    'return': '{ENTER}',
    'tab': '{TAB}',
    'space': ' ',
    'backspace': '{BACKSPACE}',
    'delete': '{DELETE}',
    'escape': '{ESC}',
    'esc': '{ESC}',
    'up': '{UP}',
    'down': '{DOWN}',
    'left': '{LEFT}',
    'right': '{RIGHT}',
    'home': '{HOME}',
    'end': '{END}',
    'pageup': '{PGUP}',
    'pagedown': '{PGDN}',
    'insert': '{INSERT}',
    'f1': '{F1}',
    'f2': '{F2}',
    'f3': '{F3}',
    'f4': '{F4}',
    'f5': '{F5}',
    'f6': '{F6}',
    'f7': '{F7}',
    'f8': '{F8}',
    'f9': '{F9}',
    'f10': '{F10}',
    'f11': '{F11}',
    'f12': '{F12}',
  };
  
  return keyMap[key] || key;
} 