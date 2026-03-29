const fs = require("fs");
const path = require("path");
const PizZip = require("pizzip");
const Docxtemplater = require("docxtemplater");

function main() {
  const [, , templatePath, payloadPath, outputPath] = process.argv;

  if (!templatePath || !payloadPath || !outputPath) {
    console.error("Usage: node render_docx.js <template.docx> <payload.json> <output.docx>");
    process.exit(1);
  }

  const templateBinary = fs.readFileSync(templatePath, "binary");
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));

  const zip = new PizZip(templateBinary);

  const doc = new Docxtemplater(zip, {
    paragraphLoop: true,
    linebreaks: true,
  });

  doc.render(payload);

  const outputBuffer = doc.getZip().generate({
    type: "nodebuffer",
    compression: "DEFLATE",
  });

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, outputBuffer);

  console.log(`DOCX written to ${outputPath}`);
}

try {
  main();
} catch (error) {
  console.error("DOCX rendering error:");

  if (error.properties && error.properties.errors) {
    for (const err of error.properties.errors) {
      console.error(err);
    }
  } else {
    console.error(error);
  }

  process.exit(1);
}