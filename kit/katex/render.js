// Build-time KaTeX: stdin = JSON [[tex, display], ...], stdout = JSON [html, ...]. A TeX error exits 1 naming the formula.
const katex = require('./katex.min.js');
let input = '';
process.stdin.on('data', (d) => (input += d)).on('end', () => {
  const errors = [], out = JSON.parse(input).map(([tex, display]) => {
    try { return katex.renderToString(tex, { displayMode: display, throwOnError: true, strict: 'ignore', output: 'htmlAndMathml' }); }
    catch (e) { errors.push(`${display ? '$$' : '$'}${tex}${display ? '$$' : '$'}: ${e.message}`); return ''; }
  });
  if (errors.length) { process.stderr.write(errors.join('\n') + '\n'); process.exit(1); }
  process.stdout.write(JSON.stringify(out));
});
