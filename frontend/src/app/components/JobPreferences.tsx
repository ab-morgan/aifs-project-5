import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

interface JobPreferencesProps {
  preferences: string;
  onPreferencesChange: (text: string) => void;
  exclusions: string;
  onExclusionsChange: (text: string) => void;
  matchCount: string;
  onMatchCountChange: (count: string) => void;
}

export function JobPreferences({
  preferences,
  onPreferencesChange,
  exclusions,
  onExclusionsChange,
  matchCount,
  onMatchCountChange,
}: JobPreferencesProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="mb-2">Job Preferences</h3>
        <p className="text-[13px] text-[#666] mb-4">Specify what you're looking for</p>
        <Textarea
          placeholder="e.g., Remote work, product companies, tech stack..."
          value={preferences}
          onChange={(e) => onPreferencesChange(e.target.value)}
          className="min-h-[100px] border-[#E5E5E5] bg-white resize-none text-[14px]"
        />
      </div>

      <div>
        <h3 className="mb-2">Exclusions</h3>
        <p className="text-[13px] text-[#666] mb-4">What you want to avoid</p>
        <Textarea
          placeholder="e.g., Startups, on-call work, long commutes..."
          value={exclusions}
          onChange={(e) => onExclusionsChange(e.target.value)}
          className="min-h-[100px] border-[#E5E5E5] bg-white resize-none text-[14px]"
        />
      </div>

      <div>
        <h3 className="mb-2">Number of Matches</h3>
        <p className="text-[13px] text-[#666] mb-4">How many results to return</p>
        <Select value={matchCount} onValueChange={onMatchCountChange}>
          <SelectTrigger className="w-full border-[#E5E5E5] bg-white">
            <SelectValue placeholder="Select count" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="5">5 matches</SelectItem>
            <SelectItem value="10">10 matches</SelectItem>
            <SelectItem value="15">15 matches</SelectItem>
            <SelectItem value="20">20 matches</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
