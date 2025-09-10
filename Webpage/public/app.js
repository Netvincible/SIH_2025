document.getElementById("uploadBtn").onclick = async () => {
    const file = document.getElementById("photoInput").files[0];
    if (!file) {
        alert("Please select a photo first!");
        return;
    }

    const formData = new FormData();
    formData.append("photo", file);

    const res = await fetch("/students", { method: "POST", body: formData });
    const data = await res.json();

    if (data.error) {
        document.getElementById("status").innerText = "❌ Upload failed";
    } else {
        document.getElementById("status").innerText = "✅ Uploaded successfully!";
        const img = document.getElementById("preview");
        img.src = data.filePath; // preview uploaded photo
        img.style.display = "block";
    }
};

document.getElementById("attendenceBtn").onclick = async () => {
  try {
    // ✅ Fix spelling and method
    const res = await fetch("/attendance", { method: "GET" });
    const data = await res.json();

    if (data.error) {
      document.getElementById("para").innerText = "❌ Could not fetch attendance";
    } else {
      document.getElementById("para").innerText = "✅ Attendance fetched!";

      const text = data.map(a =>
      `Roll No: ${a.roll_no}, Name: ${a.name}, Status: ${a.status}`)
      .join("<br>");
        //alert("Attendance: " + JSON.stringify(data.attendance));
        document.getElementById("para").innerHTML = text;
    }
  } catch (err) {
    console.error("❌ Fetch error:", err);
    document.getElementById("para").innerText = "❌ Server error";
  }
};

