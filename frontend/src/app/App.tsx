import { useState } from "react";
import { SearchSidebar } from "./components/SearchSidebar";
import { JobResults } from "./components/JobResults";
import { JobMatch } from "./components/JobResultCard";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";
import { fetchMatches } from "../api/client";

export default function App() {
  const [resumeText, setResumeText] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [preferences, setPreferences] = useState("");
  const [exclusions, setExclusions] = useState("");
  const [matchCount, setMatchCount] = useState("10");
  const [results, setResults] = useState<JobMatch[]>([]);
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [interestProfile, setInterestProfile] = useState<Record<string, number> | null>(null);

  const handleFileUpload = (file: File) => {
    setFileName(file.name);
  };

  const handleClearResume = () => {
    setResumeText("");
    setFileName(null);
  };

  const handleSearch = async () => {
    if (!resumeText.trim()) {
      toast.error("Please upload or paste your resume first");
      return;
    }

    setIsLoading(true);
    setResults([]);
    setSelectedJobs(new Set());

    try {
      const data = await fetchMatches({
        resume_text: resumeText,
        preferences: preferences || undefined,
        exclusions: exclusions || undefined,
        match_count: parseInt(matchCount),
      });
      setResults(data);
      if (data.length === 0) {
        toast.info("No matches found. Try adding more detail to your resume.");
      } else {
        toast.success(`Found ${data.length} matching job type${data.length === 1 ? "" : "s"}`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred.";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSelect = (id: string) => {
    const newSelected = new Set(selectedJobs);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedJobs(newSelected);
  };

  const handleSelectAll = () => {
    setSelectedJobs(new Set(results.map((job) => job.id)));
  };

  const handleDeselectAll = () => {
    setSelectedJobs(new Set());
  };

  const handleExport = () => {
    const selectedResults = results.filter((job) => selectedJobs.has(job.id));

    let exportText = "CAREER MATCH RESULTS - JOB TYPE ANALYSIS\n";
    exportText += "Generated: " + new Date().toLocaleString() + "\n";
    exportText += "=".repeat(100) + "\n\n";

    selectedResults.forEach((job, index) => {
      exportText += `${index + 1}. ${job.jobTitle} (${job.matchPercentage}% Match)\n\n`;
      exportText += `Description:\n${job.jobDescription}\n\n`;
      exportText += `Match Reason:\n${job.matchReason}\n\n`;
      exportText += `Job Insights:\n`;

      const { insights } = job;
      exportText += `  • Percent of Database: ${insights.percentOfDatabase != null ? insights.percentOfDatabase.toFixed(2) + "%" : "N/A"}\n`;
      exportText += `  • Frequency Rank: ${insights.frequencyRank != null ? "#" + insights.frequencyRank : "N/A"}\n`;
      exportText += `  • Average Tenure: ${insights.averageTenure != null ? insights.averageTenure.toFixed(1) + " years" : "N/A"}\n`;
      exportText += `  • Median Tenure: ${insights.medianTenure != null ? insights.medianTenure.toFixed(1) + " years" : "N/A"}\n`;
      exportText += `  • Top Career Transitions:\n`;
      insights.topTransitions.forEach((transition, i) => {
        exportText += `    ${i + 1}. ${transition.jobTitle} — ${transition.percentage.toFixed(1)}%\n`;
      });

      exportText += "\n" + "-".repeat(100) + "\n\n";
    });

    const blob = new Blob([exportText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `career-matches-${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success(`Exported ${selectedResults.length} job ${selectedResults.length === 1 ? "type" : "types"}`);
  };

  const handleInterestProfileComplete = (profile: Record<string, number>) => {
    setInterestProfile(profile);
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] flex">
      <Toaster />

      {/* Sidebar */}
      <SearchSidebar
        resumeText={resumeText}
        onResumeTextChange={setResumeText}
        fileName={fileName}
        onFileUpload={handleFileUpload}
        preferences={preferences}
        onPreferencesChange={setPreferences}
        exclusions={exclusions}
        onExclusionsChange={setExclusions}
        matchCount={matchCount}
        onMatchCountChange={setMatchCount}
        onSearch={handleSearch}
        isLoading={isLoading}
        interestProfile={interestProfile}
        onInterestProfileComplete={handleInterestProfileComplete}
        onClearResume={handleClearResume}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-[#E5E5E5] bg-white px-12 py-6 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#1B2D4F] rounded flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-[#1B2D4F]">Career Match AI</h1>
          </div>
        </header>

        {/* Results Area */}
        <main className="flex-1 overflow-y-auto px-12 py-8">
          <JobResults
            results={results}
            selectedJobs={selectedJobs}
            onToggleSelect={handleToggleSelect}
            onSelectAll={handleSelectAll}
            onDeselectAll={handleDeselectAll}
            onExport={handleExport}
            isLoading={isLoading}
          />
        </main>
      </div>
    </div>
  );
}
