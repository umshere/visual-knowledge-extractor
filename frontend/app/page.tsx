"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type ExtractedImageInfo = {
  image_id: string;
  filename: string;
  slide_index: number;
  ocr_text?: string | null;
};

type SlideInfo = {
  slide_index: number;
  title?: string | null;
  text_items: string[];
  notes?: string | null;
  images: ExtractedImageInfo[];
};

type KnowledgeDoc = {
  source_filename: string;
  slide_count: number;
  slides: SlideInfo[];
};

type JobStatus = {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  message?: string | null;
  progress: number;
  result?: KnowledgeDoc | null;
  error?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Home() {
  const [dragActive, setDragActive] = useState(false);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const statusClass = useMemo(() => {
    if (!job) return "";
    return `status ${job.status}`;
  }, [job]);

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.name.endsWith(".pptx")) {
      setError("Only .pptx files are supported.");
      return;
    }

    setError(null);
    setUploading(true);
    setJob(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || "Upload failed");
      }
      const data = await response.json();
      setJob({
        job_id: data.jobId,
        status: "queued",
        message: "Queued",
        progress: 0,
        result: null,
        error: null
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, []);

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragActive(false);
      handleFiles(event.dataTransfer.files);
    },
    [handleFiles]
  );

  useEffect(() => {
    if (!job?.job_id) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/api/job/${job.job_id}`);
        if (!response.ok) {
          throw new Error("Failed to fetch job status");
        }
        const data: JobStatus = await response.json();
        setJob(data);
        if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Polling failed");
        clearInterval(interval);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [job?.job_id]);

  const handleBrowse = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(event.target.files);
    },
    [handleFiles]
  );

  const downloadUrl = job?.job_id
    ? `${API_BASE}/api/job/${job.job_id}/download`
    : null;

  return (
    <main>
      <header>
        <h1>PPT Knowledge Doc</h1>
        <p>
          Drag and drop a .pptx to extract slide text, speaker notes, and OCR from images. The backend will
          produce a structured knowledge JSON and a downloadable Markdown document.
        </p>
      </header>

      <section className="card">
        <div
          className={`dropzone ${dragActive ? "active" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <input ref={fileInputRef} type="file" accept=".pptx" onChange={handleInputChange} />
          <p>Drop your .pptx here</p>
          <p>
            <small>or</small>
          </p>
          <button className="button" type="button" onClick={handleBrowse} disabled={uploading}>
            {uploading ? "Uploading..." : "Browse file"}
          </button>
        </div>
        {error && (
          <p style={{ color: "var(--danger)", marginTop: "16px" }}>{error}</p>
        )}
      </section>

      {job && (
        <section className="card">
          <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
            <div>
              <div className="badge">
                <span className={statusClass}>Status: {job.status}</span>
              </div>
              <p style={{ marginTop: "8px" }}>{job.message}</p>
            </div>
            {downloadUrl && job.status === "completed" && (
              <a className="button secondary" href={downloadUrl}>
                Download Markdown
              </a>
            )}
          </div>
          <div className="progress" style={{ marginTop: "16px" }}>
            <div style={{ width: `${Math.round(job.progress * 100)}%` }} />
          </div>
        </section>
      )}

      {job?.result && (
        <section className="card">
          <h2>Extracted Knowledge Document</h2>
          <p style={{ marginTop: "8px" }}>
            Source: {job.result.source_filename} · Slides: {job.result.slide_count}
          </p>
          <div style={{ marginTop: "20px", display: "grid", gap: "16px" }}>
            {job.result.slides.map((slide) => (
              <div key={slide.slide_index} className="slide">
                <h3>Slide {slide.slide_index}</h3>
                {slide.title && <p><strong>Title:</strong> {slide.title}</p>}
                {slide.text_items.length > 0 && (
                  <div>
                    <p><strong>Text:</strong></p>
                    <ul>
                      {slide.text_items.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {slide.notes && (
                  <p><strong>Notes:</strong> {slide.notes}</p>
                )}
                {slide.images.length > 0 && (
                  <div>
                    <p><strong>Images:</strong></p>
                    <ul>
                      {slide.images.map((image) => (
                        <li key={image.image_id}>
                          {image.filename.split("/").slice(-1)[0]}
                          {image.ocr_text && (
                            <div><small>OCR: {image.ocr_text}</small></div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
