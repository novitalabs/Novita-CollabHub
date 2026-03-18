import { Button } from "@/components/ui/button";
import { useSnakeGame } from "@/hooks/useSnakeGame";
import { cn } from "@/lib/utils";
import { Trophy, Play, RotateCcw, Pause } from "lucide-react";

export default function Home() {
  const {
    snake,
    food,
    status,
    score,
    highScore,
    resetGame,
    setStatus,
    boardSize
  } = useSnakeGame(20);

  // Calculate grid cell size based on viewport (responsive)
  // We'll use CSS Grid for the board
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* CRT Scanline Overlay */}
      <div className="scanlines pointer-events-none z-50"></div>
      
      {/* Background Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(57,255,20,0.1)_0%,transparent_70%)] pointer-events-none"></div>

      <div className="z-10 w-full max-w-2xl px-4 flex flex-col items-center gap-8">
        
        {/* Header / Score Board */}
        <div className="w-full flex justify-between items-end border-b-2 border-[var(--color-neon-purple)] pb-4 glow-box bg-black/50 p-6 rounded-lg backdrop-blur-sm">
          <div className="flex flex-col gap-1">
            <h1 className="text-4xl text-[var(--color-neon-blue)] glow-text tracking-widest uppercase">
              Neon Snake
            </h1>
            <div className="flex items-center gap-2 text-[var(--color-neon-yellow)]">
              <Trophy size={16} />
              <span className="text-xl">HI-SCORE: {highScore.toString().padStart(5, '0')}</span>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-sm text-muted-foreground uppercase tracking-wider">Score</div>
            <div className="text-5xl font-arcade text-[var(--color-neon-green)] glow-text">
              {score.toString().padStart(5, '0')}
            </div>
          </div>
        </div>

        {/* Game Board Container */}
        <div className="relative p-1 bg-[var(--color-neon-purple)] rounded-sm shadow-[0_0_20px_var(--color-neon-purple)]">
          <div 
            className="bg-black grid gap-[1px]"
            style={{
              gridTemplateColumns: `repeat(${boardSize}, 1fr)`,
              width: 'min(80vw, 500px)',
              height: 'min(80vw, 500px)',
            }}
          >
            {Array.from({ length: boardSize * boardSize }).map((_, i) => {
              const x = i % boardSize;
              const y = Math.floor(i / boardSize);
              
              const isSnakeHead = snake[0].x === x && snake[0].y === y;
              const isSnakeBody = snake.some((s, idx) => idx !== 0 && s.x === x && s.y === y);
              const isFood = food.x === x && food.y === y;

              return (
                <div 
                  key={i} 
                  className={cn(
                    "w-full h-full relative",
                    "border-[0.5px] border-white/5", // Faint grid lines
                    isSnakeBody && "bg-[var(--color-neon-green)] shadow-[0_0_10px_var(--color-neon-green)]",
                    isSnakeHead && "bg-white shadow-[0_0_15px_white] z-10",
                    isFood && "bg-[var(--color-neon-pink)] animate-pulse shadow-[0_0_10px_var(--color-neon-pink)] rounded-full scale-75"
                  )}
                >
                  {isSnakeHead && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-[60%] h-[60%] bg-black/20" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Game Over Overlay */}
          {status === 'GAME_OVER' && (
            <div className="absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-20 backdrop-blur-sm">
              <h2 className="text-6xl text-[var(--color-neon-pink)] glow-text mb-4 animate-pulse">GAME OVER</h2>
              <p className="text-xl text-white mb-8 font-terminal">FINAL SCORE: {score}</p>
              <Button 
                onClick={resetGame}
                className="bg-[var(--color-neon-green)] text-black hover:bg-white hover:scale-105 transition-all font-arcade text-lg px-8 py-6 shadow-[0_0_20px_var(--color-neon-green)]"
              >
                <RotateCcw className="mr-2 h-5 w-5" />
                TRY AGAIN
              </Button>
            </div>
          )}

          {/* Start Overlay */}
          {status === 'IDLE' && (
            <div className="absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-20 backdrop-blur-sm">
              <h2 className="text-4xl text-[var(--color-neon-blue)] glow-text mb-8 text-center leading-relaxed">
                READY PLAYER ONE?
              </h2>
              <Button 
                onClick={resetGame}
                className="bg-[var(--color-neon-blue)] text-black hover:bg-white hover:scale-105 transition-all font-arcade text-lg px-8 py-6 shadow-[0_0_20px_var(--color-neon-blue)]"
              >
                <Play className="mr-2 h-5 w-5" />
                INSERT COIN (START)
              </Button>
              <p className="mt-6 text-white/50 text-sm font-terminal animate-pulse">
                PRESS SPACE OR BUTTON TO START
              </p>
            </div>
          )}
          
          {/* Paused Overlay */}
          {status === 'PAUSED' && (
            <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center z-20 backdrop-blur-sm">
              <h2 className="text-5xl text-[var(--color-neon-yellow)] glow-text mb-8 tracking-widest">PAUSED</h2>
              <Button 
                onClick={() => setStatus('PLAYING')}
                className="bg-[var(--color-neon-yellow)] text-black hover:bg-white hover:scale-105 transition-all font-arcade text-lg px-8 py-6 shadow-[0_0_20px_var(--color-neon-yellow)]"
              >
                <Play className="mr-2 h-5 w-5" />
                RESUME
              </Button>
            </div>
          )}
        </div>

        {/* Controls Hint */}
        <div className="flex gap-8 text-white/60 font-terminal text-lg">
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <kbd className="border border-white/20 px-2 py-1 rounded bg-white/5">↑</kbd>
              <kbd className="border border-white/20 px-2 py-1 rounded bg-white/5">↓</kbd>
              <kbd className="border border-white/20 px-2 py-1 rounded bg-white/5">←</kbd>
              <kbd className="border border-white/20 px-2 py-1 rounded bg-white/5">→</kbd>
            </div>
            <span>TO MOVE</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="border border-white/20 px-3 py-1 rounded bg-white/5">SPACE</kbd>
            <span>PAUSE / RESTART</span>
          </div>
        </div>
      </div>
    </div>
  );
}
