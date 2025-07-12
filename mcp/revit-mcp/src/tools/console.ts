import { z } from "zod";
import { type InferSchema } from "xmcp";
import { readdir, readFile, stat } from 'fs/promises';
import { join } from 'path';
import { homedir } from 'os';

// Define the schema for tool parameters
export const schema = {
  action: z.enum(['list', 'read_latest', 'read_file', 'tail']).describe('Action to perform: list journal files, read latest journal, read specific file, or tail latest journal'),
  filename: z.string().optional().describe('Specific journal filename to read (only required for read_file action)'),
  lines: z.number().min(1).max(1000).default(50).describe('Number of lines to read from the end (for tail action, default: 50)')
};

// Define tool metadata
export const metadata = {
  name: "revit_journals",
  description: "Access Revit journal files from the current session only. Provides secure, read-only access to Revit's journal files for debugging and monitoring purposes.",
  annotations: {
    title: "Revit Journals",
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
  },
};

async function getRevitJournalsPath(): Promise<string> {
  const userHome = homedir();
  return join(userHome, 'AppData', 'Local', 'Autodesk', 'Revit', 'Autodesk Revit 2026', 'Journals');
}

async function getCurrentSessionJournals(): Promise<string[]> {
  const journalsPath = await getRevitJournalsPath();
  
  try {
    const files = await readdir(journalsPath);
    const journalFiles = files.filter(file => file.endsWith('.txt') || file.endsWith('.log'));
    
    // Get file stats to sort by modification time (most recent first)
    const filesWithStats = await Promise.all(
      journalFiles.map(async (file) => {
        const filePath = join(journalsPath, file);
        const stats = await stat(filePath);
        return { file, mtime: stats.mtime };
      })
    );
    
    // Sort by modification time, most recent first
    filesWithStats.sort((a, b) => b.mtime.getTime() - a.mtime.getTime());
    
    return filesWithStats.map(item => item.file);
  } catch (error) {
    throw new Error(`Cannot access Revit journals directory: ${error}`);
  }
}

async function readJournalFile(filename: string): Promise<string> {
  const journalsPath = await getRevitJournalsPath();
  const filePath = join(journalsPath, filename);
  
  // Security check: ensure the file is within the journals directory
  if (!filePath.startsWith(journalsPath)) {
    throw new Error('Access denied: file must be within Revit journals directory');
  }
  
  try {
    const content = await readFile(filePath, 'utf8');
    return content;
  } catch (error) {
    throw new Error(`Cannot read journal file ${filename}: ${error}`);
  }
}

async function tailJournalFile(filename: string, lines: number = 50): Promise<string> {
  const journalsPath = await getRevitJournalsPath();
  const filePath = join(journalsPath, filename);
  
  // Security check: ensure the file is within the journals directory
  if (!filePath.startsWith(journalsPath)) {
    throw new Error('Access denied: file must be within Revit journals directory');
  }
  
  try {
    const content = await readFile(filePath, 'utf8');
    const allLines = content.split('\n');
    const lastLines = allLines.slice(-lines);
    return lastLines.join('\n');
  } catch (error) {
    throw new Error(`Cannot tail journal file ${filename}: ${error}`);
  }
}

// Tool implementation
export default async function revitJournals({ action, filename, lines = 50 }: InferSchema<typeof schema>) {
  try {
    switch (action) {
      case 'list':
        const journals = await getCurrentSessionJournals();
        return {
          content: [
            {
              type: 'text',
              text: `Available Revit journal files (sorted by most recent):\n${journals.join('\n')}`
            }
          ]
        };
      
      case 'read_latest':
        const latestJournals = await getCurrentSessionJournals();
        if (latestJournals.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No journal files found'
              }
            ]
          };
        }
        
        const latestContent = await readJournalFile(latestJournals[0]);
        return {
          content: [
            {
              type: 'text',
              text: `Latest journal file: ${latestJournals[0]}\n\n${latestContent}`
            }
          ]
        };
      
      case 'read_file':
        if (!filename) {
          return {
            content: [
              {
                type: 'text',
                text: 'Error: filename is required for read_file action'
              }
            ]
          };
        }
        
        const fileContent = await readJournalFile(filename);
        return {
          content: [
            {
              type: 'text',
              text: `Journal file: ${filename}\n\n${fileContent}`
            }
          ]
        };
      
      case 'tail':
        const tailJournals = await getCurrentSessionJournals();
        if (tailJournals.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No journal files found'
              }
            ]
          };
        }
        
        const tailContent = await tailJournalFile(tailJournals[0], lines);
        return {
          content: [
            {
              type: 'text',
              text: `Last ${lines} lines of ${tailJournals[0]}:\n\n${tailContent}`
            }
          ]
        };
      
      default:
        return {
          content: [
            {
              type: 'text',
              text: 'Error: Invalid action. Use: list, read_latest, read_file, or tail'
            }
          ]
        };
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ]
    };
  }
}