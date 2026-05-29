import { useState } from "react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./ui/dialog";
import { RadioGroup, RadioGroupItem } from "./ui/radio-group";
import { Label } from "./ui/label";

interface InterestQuestionnaireProps {
  onComplete: (results: Record<string, number>) => void;
}

// Sample O*NET interest profiler questions (simplified)
const questions = [
  {
    id: 1,
    category: "Realistic",
    text: "Build kitchen cabinets or other furniture",
  },
  {
    id: 2,
    category: "Investigative",
    text: "Study ways to reduce water pollution",
  },
  {
    id: 3,
    category: "Artistic",
    text: "Write stories or articles for magazines",
  },
  {
    id: 4,
    category: "Social",
    text: "Teach an individual an exercise routine",
  },
  {
    id: 5,
    category: "Enterprising",
    text: "Manage a retail store",
  },
  {
    id: 6,
    category: "Conventional",
    text: "Organize and schedule office meetings",
  },
  {
    id: 7,
    category: "Realistic",
    text: "Repair household appliances",
  },
  {
    id: 8,
    category: "Investigative",
    text: "Conduct chemical experiments",
  },
  {
    id: 9,
    category: "Artistic",
    text: "Create animations for video games",
  },
  {
    id: 10,
    category: "Social",
    text: "Help people with personal or emotional problems",
  },
  {
    id: 11,
    category: "Enterprising",
    text: "Buy and sell stocks and bonds",
  },
  {
    id: 12,
    category: "Conventional",
    text: "Keep shipping and receiving records",
  },
];

export function InterestQuestionnaire({ onComplete }: InterestQuestionnaireProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});

  const handleAnswer = (value: string) => {
    const newAnswers = { ...answers, [currentQuestion]: parseInt(value) };
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setTimeout(() => {
        setCurrentQuestion(currentQuestion + 1);
      }, 200);
    } else {
      // Calculate results
      const categoryScores: Record<string, number> = {
        Realistic: 0,
        Investigative: 0,
        Artistic: 0,
        Social: 0,
        Enterprising: 0,
        Conventional: 0,
      };

      questions.forEach((question, index) => {
        if (newAnswers[index]) {
          categoryScores[question.category] += newAnswers[index];
        }
      });

      setTimeout(() => {
        onComplete(categoryScores);
        setIsOpen(false);
        setCurrentQuestion(0);
        setAnswers({});
      }, 500);
    }
  };

  const handleStart = () => {
    setIsOpen(true);
    setCurrentQuestion(0);
    setAnswers({});
  };

  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <>
      <Button
        variant="outline"
        onClick={handleStart}
        className="w-full border-[#E5E5E5] bg-white hover:bg-[#F5F5F5]"
      >
        Take O*NET Interest Questionnaire
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>O*NET Interest Profiler</DialogTitle>
            <DialogDescription>
              Question {currentQuestion + 1} of {questions.length}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            <div className="w-full bg-[#E5E5E5] h-2 rounded-full overflow-hidden">
              <div
                className="bg-[#1B2D4F] h-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="py-6">
              <p className="mb-6">
                How would you feel about this activity?
              </p>
              <p className="text-[15px] mb-8 p-4 bg-[#F9FAFB] rounded border border-[#E5E5E5]">
                {questions[currentQuestion].text}
              </p>

              <RadioGroup
                value={answers[currentQuestion]?.toString()}
                onValueChange={handleAnswer}
              >
                <div className="space-y-3">
                  <div className="flex items-center space-x-3 p-4 border border-[#E5E5E5] rounded hover:bg-[#F9FAFB] cursor-pointer">
                    <RadioGroupItem value="5" id="r5" />
                    <Label htmlFor="r5" className="cursor-pointer flex-1">
                      Strongly Like
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-4 border border-[#E5E5E5] rounded hover:bg-[#F9FAFB] cursor-pointer">
                    <RadioGroupItem value="4" id="r4" />
                    <Label htmlFor="r4" className="cursor-pointer flex-1">
                      Like
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-4 border border-[#E5E5E5] rounded hover:bg-[#F9FAFB] cursor-pointer">
                    <RadioGroupItem value="3" id="r3" />
                    <Label htmlFor="r3" className="cursor-pointer flex-1">
                      Unsure
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-4 border border-[#E5E5E5] rounded hover:bg-[#F9FAFB] cursor-pointer">
                    <RadioGroupItem value="2" id="r2" />
                    <Label htmlFor="r2" className="cursor-pointer flex-1">
                      Dislike
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-4 border border-[#E5E5E5] rounded hover:bg-[#F9FAFB] cursor-pointer">
                    <RadioGroupItem value="1" id="r1" />
                    <Label htmlFor="r1" className="cursor-pointer flex-1">
                      Strongly Dislike
                    </Label>
                  </div>
                </div>
              </RadioGroup>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
