import express from "express";
import multer from "multer";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import mysql from "mysql2"; 

// Setup __dirname in ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Ensure uploads folder exists
const uploadDir = path.join(__dirname, "students");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "",
  database:"schoolDB"
});

db.connect((err) => {
  if (err) {
    console.error("❌ Database connection failed:", err);
    return;
  }
  console.log("✅ Connected to the database.");
});

// Configure multer storage
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

// File filter (allow only images)
function fileFilter(req, file, cb) {
  const allowed = /jpeg|jpg/;
  const ext = path.extname(file.originalname).toLowerCase();
  if (allowed.test(ext)) {
    cb(null, true);
  } else {
    cb(new Error("Only image files are allowed!"));
  }
}

const upload = multer({ storage, fileFilter });

// Serve static frontend and uploaded files
app.use(express.static(path.join(__dirname, "public")));
app.use("/students", express.static(uploadDir));

// Route to handle upload
app.post("/students", upload.single("photo"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No photo uploaded" });
  }

  console.log("✅ Photo uploaded:", req.file);

  res.json({
    message: "Photo uploaded successfully!",
    filePath: `/students/${req.file.filename}`
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error("❌ Error:", err.message);
  res.status(500).json({ error: err.message });
});

app.get("/attendance", (req, res) => {
  const query = "SELECT roll_no, name, total_lectures, present, absent FROM attendance";
  db.query(query, (err, results) => {
    if (err) {
      console.error("❌ Database query error:", err);
      return res.status(500).json({ error: "Database query error" });
    }
    res.json(results);
  });
});

// Start server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});