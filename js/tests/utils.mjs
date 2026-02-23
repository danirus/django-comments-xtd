export async function enrichPage(page) {
  // Step 1: Expose a function to Node.js to receive logs from the browser
  await page.exposeFunction('forwardLogToNode', (logType, ...args) => {
    if (logType === 'table') {
        console.log(`[TABLE]`);
        console.table(args[0]); // args[0] is the table data
      } else {
      console.log(`[${logType.toUpperCase()}]`, ...args);
    }
  });

  // Step 2: Override browser console methods to forward logs to Node.js
  await page.evaluateOnNewDocument(() => {
    // Override all console methods (log, info, warn, error, table, etc.)
    ['log', 'info', 'warn', 'error', 'table'].forEach((method) => {
      const originalConsoleMethod = console[method];
      console[method] = (...args) => {
        // Forward logs to Node.js via the exposed function
        window.forwardLogToNode(method, ...args);
        // Preserve original browser behavior (optional)
        originalConsoleMethod(...args);
      };
    });
  });
}
