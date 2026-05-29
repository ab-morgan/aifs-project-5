import { Upload, X } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { InterestQuestionnaire } from "./InterestQuestionnaire";
import { toast } from "sonner";

interface SearchSidebarProps {
  resumeText: string;
  onResumeTextChange: (text: string) => void;
  fileName: string | null;
  onFileUpload: (file: File) => void;
  preferences: string;
  onPreferencesChange: (text: string) => void;
  exclusions: string;
  onExclusionsChange: (text: string) => void;
  matchCount: string;
  onMatchCountChange: (count: string) => void;
  onSearch: () => void;
  isLoading: boolean;
  interestProfile: Record<string, number> | null;
  onInterestProfileComplete: (results: Record<string, number>) => void;
  onClearResume: () => void;
}

export function SearchSidebar({
  resumeText,
  onResumeTextChange,
  fileName,
  onFileUpload,
  preferences,
  onPreferencesChange,
  exclusions,
  onExclusionsChange,
  matchCount,
  onMatchCountChange,
  onSearch,
  isLoading,
  interestProfile,
  onInterestProfileComplete,
  onClearResume,
}: SearchSidebarProps) {
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

  const handleQuestionnaireComplete = (results: Record<string, number>) => {
    onInterestProfileComplete(results);
    toast.success("Interest profile completed");
  };

  return (
    <div className="w-[380px] border-r border-[#E5E5E5] bg-white h-screen sticky top-0 overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Resume Section */}
        <div>
          <h3 className="mb-3">Resume</h3>
          
          {!fileName && !resumeText && (
            <>
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
                  className="w-full h-20 border-2 border-dashed border-[#D0D0D0] bg-[#FAFAFA] hover:bg-[#F5F5F5] hover:border-[#1B2D4F]"
                  onClick={() => document.getElementById('resume-upload')?.click()}
                >
                  <div className="flex flex-col items-center gap-2">
                    <Upload className="w-4 h-4 text-[#666]" />
                    <span className="text-[13px] text-[#666]">Upload resume</span>
                  </div>
                </Button>
              </label>

              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-[#E5E5E5]" />
                </div>
                <div className="relative flex justify-center">
                  <span className="bg-white px-2 text-[11px] text-[#999]">OR</span>
                </div>
              </div>

              <Textarea
                placeholder="Paste resume text..."
                value={resumeText}
                onChange={(e) => onResumeTextChange(e.target.value)}
                className="min-h-[120px] border-[#E5E5E5] bg-white resize-none text-[13px]"
              />
            </>
          )}

          {(fileName || resumeText) && (
            <div className="border border-[#E5E5E5] rounded-lg p-4 bg-[#F9FAFB]">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-medium text-[#1B2D4F] truncate">
                    {fileName || "Pasted resume text"}
                  </p>
                  <p className="text-[11px] text-[#666] mt-1">
                    {resumeText.length} characters
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClearResume}
                  className="h-6 w-6 p-0 hover:bg-[#E5E5E5]"
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="h-px bg-[#E5E5E5]" />

        {/* Interest Profile */}
        <div>
          <h3 className="mb-2">Interest Profile</h3>
          <p className="text-[11px] text-[#666] mb-3">
            Optional: Complete questionnaire for better matches
          </p>
          
          {interestProfile ? (
            <div className="border border-[#E5E5E5] rounded-lg p-3 bg-[#F9FAFB] mb-3">
              <p className="text-[11px] text-[#1B2D4F] font-medium mb-2">Profile completed ✓</p>
              <div className="space-y-1">
                {Object.entries(interestProfile)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 3)
                  .map(([category, score]) => (
                    <div key={category} className="flex justify-between text-[11px]">
                      <span className="text-[#666]">{category}</span>
                      <span className="text-[#333]">{score}</span>
                    </div>
                  ))}
              </div>
            </div>
          ) : null}
          
          <InterestQuestionnaire onComplete={handleQuestionnaireComplete} />
        </div>

        <div className="h-px bg-[#E5E5E5]" />

        {/* Preferences */}
        <div>
          <h3 className="mb-2">Preferences</h3>
          <p className="text-[11px] text-[#666] mb-3">What you're looking for</p>
          <Textarea
            placeholder="e.g., Remote work, product companies..."
            value={preferences}
            onChange={(e) => onPreferencesChange(e.target.value)}
            className="min-h-[80px] border-[#E5E5E5] bg-white resize-none text-[13px]"
          />
        </div>

        {/* Exclusions */}
        <div>
          <h3 className="mb-2">Exclusions</h3>
          <p className="text-[11px] text-[#666] mb-3">What to avoid</p>
          <Textarea
            placeholder="e.g., Startups, on-call work..."
            value={exclusions}
            onChange={(e) => onExclusionsChange(e.target.value)}
            className="min-h-[80px] border-[#E5E5E5] bg-white resize-none text-[13px]"
          />
        </div>

        {/* Match Count */}
        <div>
          <h3 className="mb-2">Results</h3>
          <p className="text-[11px] text-[#666] mb-3">Number of matches</p>
          <div className="grid grid-cols-4 gap-2">
            {['5', '10', '15', '20'].map((count) => (
              <Button
                key={count}
                variant={matchCount === count ? "default" : "outline"}
                size="sm"
                onClick={() => onMatchCountChange(count)}
                className={
                  matchCount === count
                    ? "bg-[#1B2D4F] hover:bg-[#2A3F5F] text-white"
                    : "border-[#E5E5E5] hover:bg-[#F5F5F5]"
                }
              >
                {count}
              </Button>
            ))}
          </div>
        </div>

        <Button
          onClick={onSearch}
          disabled={isLoading || (!resumeText && !fileName)}
          className="w-full bg-[#1B2D4F] hover:bg-[#2A3F5F] text-white h-11"
        >
          {isLoading ? "Searching..." : "Find Matches"}
        </Button>
      </div>
    </div>
  );
}
