import { z } from "zod";
import { type InferSchema } from "xmcp";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

// Define the schema for tool parameters
export const schema = {
  command: z.string().describe("Command to execute in the console"),
  timeout: z.number().min(1000).max(30000).default(5000).describe("Timeout in milliseconds (1-30 seconds)"),
  shell: z.enum(["cmd", "powershell", "bash"]).default("cmd").describe("Shell to use for execution"),
};

// Define tool metadata
export const metadata = {
  name: "console",
  description: "Execute console commands and return output. Useful for checking running processes, bringing windows to front, etc.",
  annotations: {
    title: "MCP Console",
    readOnlyHint: false,
    destructiveHint: true,
    idempotentHint: false,
  },
};

// Helper function to check if Revit is running
async function checkRevitRunning(): Promise<{ isRunning: boolean; processes: string[] }> {
  try {
    const { stdout } = await execAsync('tasklist /FI "IMAGENAME eq Revit.exe" /FO CSV', { timeout: 5000 });
    const lines = stdout.split('\n').filter(line => line.includes('Revit.exe'));
    return {
      isRunning: lines.length > 0,
      processes: lines
    };
  } catch (error) {
    console.error("Error checking Revit:", error);
    return { isRunning: false, processes: [] };
  }
}

// Helper function to bring Revit to front
async function bringRevitToFront(): Promise<{ success: boolean; message: string }> {
  try {
    // First check if Revit is running
    const revitCheck = await checkRevitRunning();
    if (!revitCheck.isRunning) {
      return { success: false, message: "Revit is not running" };
    }

    // Use PowerShell to bring Revit window to front
    const psCommand = `
Add-Type -AssemblyName Microsoft.VisualBasic
Add-Type -AssemblyName System.Windows.Forms
$revitProcess = Get-Process -Name "Revit" -ErrorAction SilentlyContinue
if ($revitProcess) {
    $revitProcess | ForEach-Object {
        if ($_.MainWindowTitle -ne "") {
            [Microsoft.VisualBasic.Interaction]::AppActivate($_.Id)
            [System.Windows.Forms.SendKeys]::SendWait("%{TAB}")
            Write-Output "Revit window brought to front: $($_.MainWindowTitle)"
        }
    }
} else {
    Write-Output "No Revit process found"
}
    `;

    const { stdout } = await execAsync(`powershell -Command "${psCommand}"`, { timeout: 10000 });
    return { success: true, message: stdout.trim() };
  } catch (error) {
    return { success: false, message: `Error bringing Revit to front: ${error instanceof Error ? error.message : String(error)}` };
  }
}

// Tool implementation
export default async function console({ command, timeout, shell }: InferSchema<typeof schema>) {
  try {
    const timestamp = Date.now();
    
    // Handle special commands
    if (command.toLowerCase() === "check-revit" || command.toLowerCase() === "revit-status") {
      const result = await checkRevitRunning();
      return {
        content: [
          {
            type: "text",
            text: `🔍 **Revit Status Check**\n\n` +
                  `**Status**: ${result.isRunning ? '✅ Running' : '❌ Not Running'}\n` +
                  `**Processes Found**: ${result.processes.length}\n\n` +
                  (result.processes.length > 0 ? 
                    `**Process Details**:\n${result.processes.join('\n')}` : 
                    'No Revit processes detected'),
          },
        ],
      };
    }

    if (command.toLowerCase() === "bring-revit-front" || command.toLowerCase() === "focus-revit") {
      const result = await bringRevitToFront();
      return {
        content: [
          {
            type: "text",
            text: `🎯 **Bring Revit to Front**\n\n` +
                  `**Result**: ${result.success ? '✅ Success' : '❌ Failed'}\n` +
                  `**Message**: ${result.message}`,
          },
        ],
      };
    }

    if (command.toLowerCase() === "help" || command.toLowerCase() === "commands") {
      return {
        content: [
          {
            type: "text",
            text: `🖥️ **MCP Console Help**\n\n` +
                  `**Special Commands**:\n` +
                  `• \`check-revit\` or \`revit-status\` - Check if Revit is running\n` +
                  `• \`bring-revit-front\` or \`focus-revit\` - Bring Revit window to front\n` +
                  `• \`help\` or \`commands\` - Show this help\n\n` +
                  `**General Commands**:\n` +
                  `• \`tasklist\` - List running processes\n` +
                  `• \`tasklist /FI "IMAGENAME eq *.exe"\` - Filter processes\n` +
                  `• \`dir\` - List directory contents\n` +
                  `• Any Windows command line command\n\n` +
                  `**Shells Available**: cmd (default), powershell, bash`,
          },
        ],
      };
    }

    // Execute regular command
    let shellCommand: string;
    switch (shell) {
      case "powershell":
        shellCommand = `powershell -Command "${command}"`;
        break;
      case "bash":
        shellCommand = `bash -c "${command}"`;
        break;
      default:
        shellCommand = command;
    }

    const { stdout, stderr } = await execAsync(shellCommand, { 
      timeout,
      maxBuffer: 5 * 1024 * 1024 // 5MB buffer
    });

    const output = stdout || stderr || "Command executed (no output)";
    
    return {
      content: [
        {
          type: "text",
          text: `💻 **Console Output** (${shell})\n\n` +
                `**Command**: \`${command}\`\n` +
                `**Executed at**: ${new Date(timestamp).toLocaleString()}\n\n` +
                `**Output**:\n\`\`\`\n${output}\n\`\`\``,
        },
      ],
    };
  } catch (error) {
    console.error("Console command error:", error);
    return {
      content: [
        {
          type: "text",
          text: `❌ **Console Error**\n\n` +
                `**Command**: \`${command}\`\n` +
                `**Shell**: ${shell}\n` +
                `**Error**: ${error instanceof Error ? error.message : String(error)}\n\n` +
                `**Tip**: Try using \`help\` to see available commands`,
        },
      ],
    };
  }
} 