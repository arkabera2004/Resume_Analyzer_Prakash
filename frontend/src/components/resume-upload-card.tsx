import { useRef, useState } from "react";
import { CheckCircle2, FileText, RotateCcw, UploadCloud } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api";
import {
  ACCEPTED_RESUME_EXTENSIONS,
  MAX_RESUME_SIZE_MB,
  isAcceptedResumeFile,
  uploadResume,
  type ResumeUploadResult,
} from "@/lib/resume";

type Status = "idle" | "uploading" | "success" | "error";

export function ResumeUploadCard() {
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<ResumeUploadResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    if (!isAcceptedResumeFile(file)) {
      toast.error("Unsupported file type", { description: "Upload a PDF or DOCX resume." });
      return;
    }
    if (file.size > MAX_RESUME_SIZE_MB * 1024 * 1024) {
      toast.error("File too large", { description: `Maximum size is ${MAX_RESUME_SIZE_MB}MB.` });
      return;
    }

    setStatus("uploading");
    setErrorMessage(null);
    try {
      const uploaded = await uploadResume(file);
      setResult(uploaded);
      setStatus("success");
      toast.success("Resume uploaded", { description: "Text extracted successfully." });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      setErrorMessage(message);
      setStatus("error");
      toast.error("Upload failed", { description: message });
    }
  }

  function handleInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = ""; // allow re-selecting the same file
    if (file) void handleFile(file);
  }

  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) void handleFile(file);
  }

  function reset() {
    setStatus("idle");
    setResult(null);
    setErrorMessage(null);
  }

  return (
    <Card className="border-border shadow-none lg:col-span-2">
      <CardHeader>
        <CardTitle>Start an analysis</CardTitle>
        <CardDescription>
          {status === "success"
            ? "Text extracted. ATS scoring and job matching are coming in a later phase."
            : "Upload a PDF or DOCX resume to extract its text — scoring and matching land next."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {status === "success" && result ? (
          <div className="space-y-4">
            <div className="flex items-start gap-3 rounded-lg border border-border bg-muted/30 px-4 py-3">
              <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-primary" />
              <div className="min-w-0">
                <p className="truncate font-medium text-foreground">{result.filename}</p>
                <p className="text-xs text-muted-foreground">
                  {result.word_count.toLocaleString()} words · {result.character_count.toLocaleString()}{" "}
                  characters extracted
                </p>
              </div>
            </div>
            <div className="rounded-lg border border-border bg-muted/20 p-4">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Extracted text preview
              </p>
              <p className="max-h-40 overflow-y-auto whitespace-pre-wrap text-sm text-foreground/80">
                {result.extracted_text.slice(0, 1000)}
                {result.extracted_text.length > 1000 ? "…" : ""}
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={reset}>
              <RotateCcw className="size-4" /> Upload a different resume
            </Button>
          </div>
        ) : (
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`flex flex-col items-center justify-center rounded-lg border border-dashed px-6 py-14 text-center transition-colors ${
              isDragging ? "border-primary bg-primary/5" : "border-border bg-muted/30"
            }`}
          >
            <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              {status === "uploading" ? (
                <FileText className="size-6 animate-pulse" />
              ) : (
                <UploadCloud className="size-6" />
              )}
            </span>
            <h3 className="mt-4 font-semibold text-foreground">
              {status === "uploading" ? "Extracting text…" : "No resume uploaded yet"}
            </h3>
            <p className="mt-2 max-w-sm text-sm text-muted-foreground">
              {status === "error" && errorMessage
                ? errorMessage
                : `PDF or DOCX, up to ${MAX_RESUME_SIZE_MB}MB.`}
            </p>
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPTED_RESUME_EXTENSIONS.join(",")}
              className="hidden"
              onChange={handleInputChange}
            />
            <Button
              className="mt-6"
              disabled={status === "uploading"}
              onClick={() => inputRef.current?.click()}
            >
              {status === "uploading" ? "Uploading…" : "Choose file"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
