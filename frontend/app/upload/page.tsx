"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";

export default function UploadPage() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [fileName, setFileName] = useState("");

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        await uploadFile(files[0]);
      }
    },
    [],
  );

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    setFileName(file.name);

    if (!file.name.endsWith(".pdf")) {
      setUploadStatus("error");
      setErrorMessage("Please upload a PDF file");
      return;
    }

    setIsUploading(true);
    setUploadStatus("uploading");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const result = await response.json();
      setUploadStatus("success");

      // Redirect to analysis page with collection_id
      setTimeout(() => {
        router.push(`/analysis?id=${result.collection_id}`);
      }, 1000);
    } catch (error) {
      setUploadStatus("error");
      setErrorMessage("Failed to upload file. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="w-full max-w-2xl mx-auto px-6 py-16 bg-[#0a0f1e] text-[#e2e8f0]">
      <Card className="w-full">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Upload Your Document</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Drag and drop a PDF file or click to browse
            </p>
          </div>

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all
              ${
                isDragging
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-gray-300 dark:border-gray-600 hover:border-blue-400"
              }
              ${
                uploadStatus === "success"
                  ? "border-green-500 bg-green-50 dark:bg-green-900/20"
                  : ""
              }
              ${
                uploadStatus === "error"
                  ? "border-red-500 bg-red-50 dark:bg-red-900/20"
                  : ""
              }
            `}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              {uploadStatus === "idle" && (
                <>
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium mb-2">
                    Drop your PDF here, or{" "}
                    <span className="text-blue-500">browse</span>
                  </p>
                  <p className="text-sm text-gray-500">
                    Only PDF files are supported
                  </p>
                </>
              )}

              {uploadStatus === "uploading" && (
                <>
                  <FileText className="mx-auto h-12 w-12 text-blue-500 mb-4 animate-pulse" />
                  <p className="text-lg font-medium">Uploading...</p>
                </>
              )}

              {uploadStatus === "success" && (
                <>
                  <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
                  <p className="text-lg font-medium text-green-600">
                    Upload successful! Redirecting...
                  </p>
                </>
              )}

              {uploadStatus === "error" && (
                <>
                  <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                  <p className="text-lg font-medium text-red-600 mb-2">
                    {errorMessage}
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => setUploadStatus("idle")}
                  >
                    Try Again
                  </Button>
                </>
              )}
            </label>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}