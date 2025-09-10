import express from "express";
import multer from "multer";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import mysql from "mysql2";
import { spawn } from "child_process"; 

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
  host: "127.0.0.1",
  user: "netvincible",
  password: "12345678",
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
//   setTimeout(function() {
//   const process=spawn("python3", ["main.py", req.file.path]);
//   let output ="";
//   process.stdout.on("data",(data)=>{
//     output+=data.toString();
//   });
// }, 2000);
  const process=spawn("python3", ["main.py", req.file.path]);
  let output ="";
  process.stdout.on("data",(data)=>{
    output+=data.toString();
  });

  process.stderr.on("data", (data) => {
    console.error("❌ Python Error:", data.toString());
  });

  process.on("close", (code) => {
    console.log(`✅ Python script exited with code ${code}`);

    res.json({
      message: "Photo uploaded successfully and Python script executed!",
      filePath: `/students/${req.file.filename}`,
      pythonOutput: output.trim()
    });
  });

  // res.json({
  //   message: "Photo uploaded successfully!",
  //   filePath: `/students/${req.file.filename}`
  // });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error("❌ Error:", err.message);
  res.status(500).json({ error: err.message });
});

app.get("/attendance", (req, res) => {
  db.query("use schoolDB;");
  const query = "SELECT roll_no, name, status from attendance_2";
  db.query(query, (err, results) => {
    if (err) {
      console.error("❌ Database query error:", err);
      return res.status(500).json({ error: "Database query error" });
    }
    res.json(results);
  });
});

// Start server
const PORT = 8080;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});