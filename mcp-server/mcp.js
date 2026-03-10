// Run with: pnpm tsx src/toolWithSampleServer.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";


const mcpServer = new McpServer({
    name: 'tools-with-sample-server',
    version: '1.0.0'
});


// Tool that uses LLM sampling to summarize any text
mcpServer.registerTool(
    'add',
    {
        title: 'Addition Tool',
        description: 'add two numbers together',
        inputSchema: z.object({
            a: z.number().describe('First number'),
            b: z.number().describe('Second number')
        })
    },
    async ({ a, b }) => {
        return {
            content: [
                {
                    type: 'text',
                    text: String(a + b)
                }
            ]
        };
    }
);


//Registering TOOLS IN MCP SERVER
mcpServer.registerTool(
    'divide',
    {
        title: 'Division Tool',
        description: 'Divide two numbers (a / b)',
        inputSchema: z.object({
            a: z.number().describe('Dividend (number to be divided)'),
            b: z.number().describe('Divisor (number to divide by)')
        })
    },
    async ({ a, b }) => {
        if (b === 0) {
            return {
                content: [
                    {
                        type: 'text',
                        text: 'Error: Division by zero is not allowed'
                    }
                ],
                isError: true
            };
        }

        return {
            content: [
                {
                    type: 'text',
                    text: String(a / b)
                }
            ]
        };
    }
);

mcpServer.registerTool(
    'summarize',
    {
        title: 'Summarize',
        description: 'Summarize any text using an LLM',
        inputSchema: z.object({
            text: z.string().describe('Text to summarize')
        })
    },
    async ({ text }) => {
        // Call the LLM through MCP sampling
        const response = await mcpServer.server.createMessage({
            messages: [
                {
                    role: 'user',
                    content: {
                        type: 'text',
                        text: `Please summarize the following text concisely:\n\n${text}`
                    }
                }
            ],
            maxTokens: 500
        });

        // Since we're not passing tools param to createMessage, response.content is single content
        return {
            content: [
                {
                    type: 'text',
                    text: response.content.type === 'text' ? response.content.text : 'Unable to generate summary'
                }
            ]
        };
    }
);


async function main() {
    const transport = new StdioServerTransport(); // How we are managing messaging out of this
    await mcpServer.connect(transport);
    //console.error('MCP server is running...');
}

try {
    await main();
} catch (error) {
    console.error('Server error:', error);
    // eslint-disable-next-line unicorn/no-process-exit
    process.exit(1);
}

