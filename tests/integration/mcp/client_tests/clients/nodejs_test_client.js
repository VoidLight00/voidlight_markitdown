#!/usr/bin/env node
/**
 * Node.js MCP Test Client for voidlight_markitdown
 * Tests STDIO and HTTP/SSE connections with comprehensive protocol validation
 */

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

// Test result class
class TestResult {
    constructor(testName, passed, duration, details, error = null) {
        this.testName = testName;
        this.passed = passed;
        this.duration = duration;
        this.details = details;
        this.error = error;
        this.timestamp = new Date().toISOString();
    }

    toJSON() {
        return {
            test_name: this.testName,
            passed: this.passed,
            duration: this.duration,
            details: this.details,
            error: this.error,
            timestamp: this.timestamp
        };
    }
}

class MCPTestClient {
    constructor(reportDir) {
        this.reportDir = reportDir;
        this.testResults = [];
        this.client = null;
    }

    async testStdioConnection() {
        const startTime = Date.now();
        const testName = "STDIO Connection Test (Node.js)";

        try {
            console.log("Testing STDIO connection...");

            // Create the transport
            const transport = new StdioClientTransport({
                command: 'python',
                args: ['-m', 'voidlight_markitdown_mcp'],
                env: {
                    ...process.env,
                    VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS: 'true',
                    VOIDLIGHT_LOG_LEVEL: 'DEBUG'
                }
            });

            // Create and connect the client
            this.client = new Client({
                name: 'nodejs-test-client',
                version: '1.0.0'
            }, {
                capabilities: {}
            });

            await this.client.connect(transport);

            // List available tools
            const toolsResponse = await this.client.listTools();
            const tools = toolsResponse.tools || [];

            const duration = (Date.now() - startTime) / 1000;

            return new TestResult(
                testName,
                true,
                duration,
                {
                    tools_count: tools.length,
                    tools: tools.map(t => ({
                        name: t.name,
                        description: t.description,
                        parameters: t.inputSchema
                    })),
                    connection_type: 'stdio'
                }
            );

        } catch (error) {
            console.error(`STDIO connection test failed: ${error}`);
            return new TestResult(
                testName,
                false,
                (Date.now() - startTime) / 1000,
                { connection_type: 'stdio' },
                error.toString()
            );
        } finally {
            if (this.client) {
                await this.client.close();
                this.client = null;
            }
        }
    }

    async testHttpSseConnection() {
        const startTime = Date.now();
        const testName = "HTTP/SSE Connection Test (Node.js)";

        try {
            console.log("Testing HTTP/SSE connection...");

            // Start the HTTP server
            const serverProcess = spawn('python', [
                '-m', 'voidlight_markitdown_mcp',
                '--http',
                '--port', '3002'
            ], {
                env: {
                    ...process.env,
                    VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS: 'true',
                    VOIDLIGHT_LOG_LEVEL: 'DEBUG'
                }
            });

            // Wait for server to start
            await new Promise(resolve => setTimeout(resolve, 2000));

            try {
                // Test HTTP endpoint
                const healthResponse = await axios.get('http://localhost:3002/', {
                    validateStatus: () => true
                });

                // Test MCP endpoint
                const mcpResponse = await axios.post('http://localhost:3002/mcp', {
                    jsonrpc: '2.0',
                    method: 'tools/list',
                    id: 1
                }, {
                    validateStatus: () => true
                });

                const duration = (Date.now() - startTime) / 1000;

                return new TestResult(
                    testName,
                    healthResponse.status < 500,
                    duration,
                    {
                        health_status: healthResponse.status,
                        mcp_response_status: mcpResponse.status,
                        mcp_data: mcpResponse.data,
                        connection_type: 'http_sse'
                    }
                );

            } finally {
                // Clean up server process
                serverProcess.kill();
            }

        } catch (error) {
            console.error(`HTTP/SSE connection test failed: ${error}`);
            return new TestResult(
                testName,
                false,
                (Date.now() - startTime) / 1000,
                { connection_type: 'http_sse' },
                error.toString()
            );
        }
    }

    async testToolInvocation(toolName, params) {
        const startTime = Date.now();
        const testName = `Tool Invocation: ${toolName} (Node.js)`;

        try {
            console.log(`Testing tool invocation: ${toolName}`);

            // Create a new connection for this test
            const transport = new StdioClientTransport({
                command: 'python',
                args: ['-m', 'voidlight_markitdown_mcp'],
                env: {
                    ...process.env,
                    VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS: 'true',
                    VOIDLIGHT_LOG_LEVEL: 'DEBUG'
                }
            });

            const client = new Client({
                name: 'nodejs-test-client',
                version: '1.0.0'
            }, {
                capabilities: {}
            });

            await client.connect(transport);

            try {
                // Call the tool
                const result = await client.callTool({
                    name: toolName,
                    arguments: params
                });

                const duration = (Date.now() - startTime) / 1000;

                return new TestResult(
                    testName,
                    true,
                    duration,
                    {
                        tool_name: toolName,
                        params: params,
                        result: result
                    }
                );

            } finally {
                await client.close();
            }

        } catch (error) {
            console.error(`Tool invocation test failed: ${error}`);
            return new TestResult(
                testName,
                false,
                (Date.now() - startTime) / 1000,
                {
                    tool_name: toolName,
                    params: params
                },
                error.toString()
            );
        }
    }

    async testKoreanTextProcessing() {
        const startTime = Date.now();
        const testName = "Korean Text Processing (Node.js)";

        try {
            console.log("Testing Korean text processing...");

            // Create test file with Korean content
            const testDir = path.join(this.reportDir, '..', 'test_files');
            await fs.mkdir(testDir, { recursive: true });
            
            const testFile = path.join(testDir, 'korean_test_nodejs.txt');
            const koreanText = `안녕하세요! Node.js 한국어 문서 테스트입니다.

# 제목 1
이것은 **굵은 글씨**이고 이것은 *기울임 글씨*입니다.

## 제목 2
- 첫 번째 항목
- 두 번째 항목
- 세 번째 항목

### 코드 예제
\`\`\`javascript
function 인사하기(이름) {
    return \`안녕하세요, \${이름}님!\`;
}
\`\`\`

[링크 텍스트](https://example.com)
`;

            await fs.writeFile(testFile, koreanText, 'utf8');

            // Test conversion
            const fileUri = `file://${testFile}`;
            
            const result = await this.testToolInvocation(
                'convert_korean_document',
                {
                    uri: fileUri,
                    normalize_korean: true
                }
            );

            // Additional validation for Korean content
            if (result.passed && result.details.result) {
                const convertedText = result.details.result.content || result.details.result;
                const koreanPreserved = 
                    convertedText.includes('안녕하세요') &&
                    convertedText.includes('한국어') &&
                    convertedText.includes('제목');

                result.details.korean_validation = {
                    korean_preserved: koreanPreserved,
                    original_length: koreanText.length,
                    converted_length: convertedText.length
                };
            }

            return result;

        } catch (error) {
            console.error(`Korean text processing test failed: ${error}`);
            return new TestResult(
                testName,
                false,
                (Date.now() - startTime) / 1000,
                {},
                error.toString()
            );
        }
    }

    async testProtocolCompliance() {
        const startTime = Date.now();
        const testName = "Protocol Compliance Test (Node.js)";

        try {
            console.log("Testing protocol compliance...");

            const complianceChecks = [];

            // Test 1: JSON-RPC 2.0 format
            const transport = new StdioClientTransport({
                command: 'python',
                args: ['-m', 'voidlight_markitdown_mcp'],
                env: {
                    ...process.env,
                    VOIDLIGHT_MARKITDOWN_ENABLE_PLUGINS: 'true',
                    VOIDLIGHT_LOG_LEVEL: 'DEBUG'
                }
            });

            const client = new Client({
                name: 'nodejs-test-client',
                version: '1.0.0'
            }, {
                capabilities: {}
            });

            await client.connect(transport);

            try {
                // Check initialize response
                complianceChecks.push({
                    check: 'Initialize Response',
                    passed: true,
                    details: 'Client initialized successfully'
                });

                // Check tools listing
                const toolsResponse = await client.listTools();
                complianceChecks.push({
                    check: 'Tools List Response',
                    passed: Array.isArray(toolsResponse.tools),
                    details: `Found ${toolsResponse.tools?.length || 0} tools`
                });

                // Check tool invocation response format
                const testResult = await client.callTool({
                    name: 'convert_to_markdown',
                    arguments: { uri: 'https://example.com' }
                });

                complianceChecks.push({
                    check: 'Tool Response Format',
                    passed: testResult !== undefined,
                    details: 'Tool returned valid response'
                });

            } finally {
                await client.close();
            }

            const allPassed = complianceChecks.every(check => check.passed);
            const duration = (Date.now() - startTime) / 1000;

            return new TestResult(
                testName,
                allPassed,
                duration,
                {
                    compliance_checks: complianceChecks,
                    total_checks: complianceChecks.length,
                    passed_checks: complianceChecks.filter(c => c.passed).length
                }
            );

        } catch (error) {
            console.error(`Protocol compliance test failed: ${error}`);
            return new TestResult(
                testName,
                false,
                (Date.now() - startTime) / 1000,
                {},
                error.toString()
            );
        }
    }

    async runAllTests() {
        console.log("Starting comprehensive MCP client tests (Node.js)...\n");

        const testSuites = [
            {
                name: "Connection Tests",
                tests: [
                    () => this.testStdioConnection(),
                    () => this.testHttpSseConnection()
                ]
            },
            {
                name: "Tool Tests",
                tests: [
                    () => this.testToolInvocation('convert_to_markdown', { uri: 'https://example.com' }),
                    () => this.testKoreanTextProcessing()
                ]
            },
            {
                name: "Compliance Tests",
                tests: [
                    () => this.testProtocolCompliance()
                ]
            }
        ];

        const allResults = [];
        const suiteSummaries = [];

        for (const suite of testSuites) {
            console.log(`\nRunning ${suite.name}...`);
            const suiteResults = [];

            for (const test of suite.tests) {
                const result = await test();
                suiteResults.push(result);
                allResults.push(result);
                this.testResults.push(result);

                // Log result
                const status = result.passed ? 'PASSED' : 'FAILED';
                console.log(`  ${result.testName}: ${status} (${result.duration.toFixed(2)}s)`);
                if (result.error) {
                    console.error(`    Error: ${result.error}`);
                }
            }

            // Suite summary
            const passed = suiteResults.filter(r => r.passed).length;
            const total = suiteResults.length;
            suiteSummaries.push({
                suite: suite.name,
                passed: passed,
                total: total,
                success_rate: total > 0 ? (passed / total * 100) : 0
            });
        }

        // Generate report
        const report = {
            timestamp: new Date().toISOString(),
            client: 'Node.js',
            summary: {
                total_tests: allResults.length,
                passed: allResults.filter(r => r.passed).length,
                failed: allResults.filter(r => !r.passed).length,
                total_duration: allResults.reduce((sum, r) => sum + r.duration, 0),
                success_rate: allResults.length > 0 
                    ? (allResults.filter(r => r.passed).length / allResults.length * 100) 
                    : 0
            },
            suite_summaries: suiteSummaries,
            test_results: allResults.map(r => r.toJSON())
        };

        // Save report
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        const reportFile = path.join(this.reportDir, `nodejs_client_test_report_${timestamp}.json`);
        await fs.writeFile(reportFile, JSON.stringify(report, null, 2));
        console.log(`\nTest report saved to: ${reportFile}`);

        return report;
    }
}

async function main() {
    const reportDir = '/Users/voidlight/voidlight_markitdown/mcp_client_tests/reports';
    await fs.mkdir(reportDir, { recursive: true });

    const client = new MCPTestClient(reportDir);
    const report = await client.runAllTests();

    // Print summary
    console.log("\n" + "=".repeat(60));
    console.log("MCP CLIENT TEST SUMMARY (Node.js)");
    console.log("=".repeat(60));
    console.log(`Total Tests: ${report.summary.total_tests}`);
    console.log(`Passed: ${report.summary.passed}`);
    console.log(`Failed: ${report.summary.failed}`);
    console.log(`Success Rate: ${report.summary.success_rate.toFixed(1)}%`);
    console.log(`Total Duration: ${report.summary.total_duration.toFixed(2)}s`);
    console.log("=".repeat(60));
}

// Run the tests
main().catch(console.error);