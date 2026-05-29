import { JobResultCard, JobMatch } from "./JobResultCard";
import { Button } from "./ui/button";
import { FileDown, Loader2 } from "lucide-react";

interface JobResultsProps {
  results: JobMatch[];
  selectedJobs: Set<string>;
  onToggleSelect: (id: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onExport: () => void;
  isLoading: boolean;
}

export function JobResults({
  results,
  selectedJobs,
  onToggleSelect,
  onSelectAll,
  onDeselectAll,
  onExport,
  isLoading,
}: JobResultsProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-32">
        <Loader2 className="w-8 h-8 text-[#1B2D4F] animate-spin mb-4" />
        <p className="text-[#666]">Analyzing resume and matching roles...</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center max-w-md">
          <p className="text-[#999] text-[15px]">
            No results yet. Upload your resume, set your preferences, and click "Find Matches" to discover matching job types.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="mb-1">Matched Job Types</h2>
          <p className="text-[13px] text-[#666]">
            {results.length} {results.length === 1 ? 'job type' : 'job types'} found
            {selectedJobs.size > 0 && ` · ${selectedJobs.size} selected for export`}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {selectedJobs.size > 0 && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={onDeselectAll}
                className="text-[13px] text-[#666] hover:text-[#1B2D4F]"
              >
                Deselect all
              </Button>
              <Button
                onClick={onExport}
                className="bg-[#1B2D4F] hover:bg-[#2A3F5F] text-white"
                size="sm"
              >
                <FileDown className="w-4 h-4 mr-2" />
                Export {selectedJobs.size} {selectedJobs.size === 1 ? 'role' : 'roles'}
              </Button>
            </>
          )}
          {selectedJobs.size === 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={onSelectAll}
              className="text-[13px]"
            >
              Select all
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {results.map((job) => (
          <JobResultCard
            key={job.id}
            job={job}
            isSelected={selectedJobs.has(job.id)}
            onToggleSelect={onToggleSelect}
          />
        ))}
      </div>
    </div>
  );
}