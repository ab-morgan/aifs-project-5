import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";
import { TrendingUp, Award, Clock } from "lucide-react";

export interface JobMatch {
  id: string;
  jobTitle: string;
  jobDescription: string;
  matchPercentage: number;
  matchReason: string;
  insights: {
    percentOfDatabase: number | null;
    frequencyRank: number | null;
    averageTenure: number | null;
    medianTenure: number | null;
    topTransitions: Array<{
      jobTitle: string;
      percentage: number;
    }>;
  };
}

interface JobResultCardProps {
  job: JobMatch;
  isSelected: boolean;
  onToggleSelect: (id: string) => void;
}

export function JobResultCard({ job, isSelected, onToggleSelect }: JobResultCardProps) {
  const getMatchColor = (percentage: number) => {
    if (percentage >= 90) return '#10B981'; // green
    if (percentage >= 75) return '#3B82F6'; // blue
    if (percentage >= 60) return '#F59E0B'; // amber
    return '#6B7280'; // gray
  };

  const matchColor = getMatchColor(job.matchPercentage);

  return (
    <div className="border border-[#E5E5E5] rounded-lg p-6 bg-white hover:shadow-md transition-all">
      {/* Header */}
      <div className="flex items-start gap-5 mb-5">
        <div className="flex-shrink-0 mt-1">
          <div className="flex flex-col items-center gap-2">
            <Checkbox
              id={`select-${job.id}`}
              checked={isSelected}
              onCheckedChange={() => onToggleSelect(job.id)}
              className="border-[#D0D0D0] w-5 h-5"
            />
            <Label 
              htmlFor={`select-${job.id}`}
              className="text-[10px] text-[#999] text-center leading-tight cursor-pointer"
            >
              Select to export
            </Label>
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-6 mb-3">
            <div className="flex-1">
              <h3 className="text-[20px] text-[#1B2D4F] mb-2">{job.jobTitle}</h3>
              <p className="text-[14px] text-[#666] leading-relaxed">
                {job.jobDescription}
              </p>
            </div>
            
            <div className="flex-shrink-0">
              <div 
                className="flex items-center justify-center w-16 h-16 rounded-full border-4"
                style={{ 
                  borderColor: matchColor,
                  backgroundColor: `${matchColor}10`
                }}
              >
                <div className="text-center">
                  <div className="font-medium" style={{ color: matchColor }}>
                    {job.matchPercentage}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Match Reason Section */}
      <div className="mb-5 p-4 bg-[#F0F4FF] rounded-md border border-[#C7D7FE]">
        <div className="flex items-start gap-2 mb-2">
          <Award className="w-4 h-4 text-[#1B2D4F] mt-0.5 flex-shrink-0" />
          <h4 className="text-[13px] text-[#1B2D4F] font-medium">Why this matches your experience</h4>
        </div>
        <p className="text-[13px] leading-relaxed text-[#333] pl-6">
          {job.matchReason}
        </p>
      </div>

      {/* Job Insights Section */}
      <div className="border-t border-[#E5E5E5] pt-5">
        <h4 className="text-[13px] text-[#1B2D4F] font-medium mb-4">Job Insights</h4>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-6 mb-5">
          <div>
            <div className="text-[11px] text-[#999] uppercase tracking-wide mb-1">
              Database %
            </div>
            <div className="text-[15px] text-[#1B2D4F] font-medium">
              {job.insights.percentOfDatabase != null ? `${job.insights.percentOfDatabase.toFixed(2)}%` : "—"}
            </div>
          </div>

          <div>
            <div className="text-[11px] text-[#999] uppercase tracking-wide mb-1">
              Frequency Rank
            </div>
            <div className="text-[15px] text-[#1B2D4F] font-medium">
              {job.insights.frequencyRank != null ? `#${job.insights.frequencyRank}` : "—"}
            </div>
          </div>

          <div>
            <div className="text-[11px] text-[#999] uppercase tracking-wide mb-1">
              Avg Tenure
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-[#666]" />
              <span className="text-[15px] text-[#1B2D4F] font-medium">
                {job.insights.averageTenure != null ? `${job.insights.averageTenure.toFixed(1)} yrs` : "—"}
              </span>
            </div>
          </div>

          <div>
            <div className="text-[11px] text-[#999] uppercase tracking-wide mb-1">
              Median Tenure
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-[#666]" />
              <span className="text-[15px] text-[#1B2D4F] font-medium">
                {job.insights.medianTenure != null ? `${job.insights.medianTenure.toFixed(1)} yrs` : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Top Transitions */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-[#666]" />
            <div className="text-[11px] text-[#999] uppercase tracking-wide">
              Top Career Transitions
            </div>
          </div>
          <div className="space-y-2 pl-6">
            {job.insights.topTransitions.map((transition, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1">
                  <span className="text-[12px] text-[#999] font-medium">
                    {index + 1}.
                  </span>
                  <span className="text-[13px] text-[#333]">
                    {transition.jobTitle}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-1.5 bg-[#F0F0F0] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[#1B2D4F] rounded-full"
                      style={{ width: `${Math.min(transition.percentage, 100)}%` }}
                    />
                  </div>
                  <span className="text-[13px] text-[#666] font-medium w-12 text-right">
                    {transition.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
