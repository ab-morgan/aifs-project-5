import { Upload } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

interface ResumeInputProps {
  resumeText: string;
  onResumeTextChange: (text: string) => void;
  fileName: string | null;
  onFileUpload: (file: File) => void;
}

export function ResumeInput({ resumeText, onResumeTextChange, fileName, onFileUpload }: ResumeInputProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
      // Simulate reading file content
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        onResumeTextChange(text);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="mb-2">Resume</h3>
        <p className="text-[13px] text-[#666] mb-4">Upload a file or paste your resume text</p>
      </div>

      <div className="border border-[#E5E5E5] rounded-lg p-6 bg-[#FAFAFA]">
        <input
          type="file"
          id="resume-upload"
          className="hidden"
          accept=".txt,.pdf,.doc,.docx"
          onChange={handleFileChange}
        />
        <label htmlFor="resume-upload">
          <Button
            type="button"
            variant="outline"
            className="w-full h-24 border-2 border-dashed border-[#D0D0D0] bg-white hover:bg-[#F5F5F5] hover:border-[#1B2D4F]"
            onClick={() => document.getElementById('resume-upload')?.click()}
          >
            <div className="flex flex-col items-center gap-2">
              <Upload className="w-5 h-5 text-[#666]" />
              <span className="text-[13px]">
                {fileName ? fileName : 'Click to upload resume'}
              </span>
            </div>
          </Button>
        </label>
      </div>

      <div className="relative">
        <div className="absolute left-4 -top-2 bg-white px-2 text-[12px] text-[#666]">
          Or paste text
        </div>
        <Textarea
          placeholder="Paste your resume text here..."
          value={resumeText}
          onChange={(e) => onResumeTextChange(e.target.value)}
          className="min-h-[240px] border-[#E5E5E5] bg-white resize-none text-[14px]"
        />
      </div>
    </div>
  );
}
