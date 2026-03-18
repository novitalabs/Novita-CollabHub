import { useCallback, useEffect, useState } from 'react';

// Types
export type Point = { x: number; y: number };
export type Direction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';
export type GameStatus = 'IDLE' | 'PLAYING' | 'PAUSED' | 'GAME_OVER';

// Constants
const GRID_SIZE = 20;
const INITIAL_SNAKE: Point[] = [
  { x: 10, y: 10 },
  { x: 10, y: 11 },
  { x: 10, y: 12 },
];
const INITIAL_DIRECTION: Direction = 'UP';
const INITIAL_SPEED = 150;

export function useSnakeGame(boardSize: number = 20) {
  const [snake, setSnake] = useState<Point[]>(INITIAL_SNAKE);
  const [food, setFood] = useState<Point>({ x: 5, y: 5 });
  const [direction, setDirection] = useState<Direction>(INITIAL_DIRECTION);
  const [nextDirection, setNextDirection] = useState<Direction>(INITIAL_DIRECTION);
  const [status, setStatus] = useState<GameStatus>('IDLE');
  const [score, setScore] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [speed, setSpeed] = useState(INITIAL_SPEED);

  // Generate random food position not on snake
  const generateFood = useCallback((currentSnake: Point[]): Point => {
    let newFood: Point;
    let isOnSnake;
    do {
      newFood = {
        x: Math.floor(Math.random() * boardSize),
        y: Math.floor(Math.random() * boardSize),
      };
      // eslint-disable-next-line no-loop-func
      isOnSnake = currentSnake.some(segment => segment.x === newFood.x && segment.y === newFood.y);
    } while (isOnSnake);
    return newFood;
  }, [boardSize]);

  // Reset Game
  const resetGame = useCallback(() => {
    setSnake(INITIAL_SNAKE);
    setDirection(INITIAL_DIRECTION);
    setNextDirection(INITIAL_DIRECTION);
    setScore(0);
    setSpeed(INITIAL_SPEED);
    setStatus('PLAYING');
    setFood(generateFood(INITIAL_SNAKE));
  }, [generateFood]);

  // Game Loop
  useEffect(() => {
    if (status !== 'PLAYING') return;

    const moveSnake = () => {
      setSnake(prevSnake => {
        const head = prevSnake[0];
        const newHead = { ...head };

        // Update direction from buffer
        setDirection(nextDirection);

        switch (nextDirection) {
          case 'UP': newHead.y -= 1; break;
          case 'DOWN': newHead.y += 1; break;
          case 'LEFT': newHead.x -= 1; break;
          case 'RIGHT': newHead.x += 1; break;
        }

        // Check collisions
        // 1. Wall collision
        if (
          newHead.x < 0 ||
          newHead.x >= boardSize ||
          newHead.y < 0 ||
          newHead.y >= boardSize
        ) {
          setStatus('GAME_OVER');
          return prevSnake;
        }

        // 2. Self collision
        if (prevSnake.some(segment => segment.x === newHead.x && segment.y === newHead.y)) {
          setStatus('GAME_OVER');
          return prevSnake;
        }

        const newSnake = [newHead, ...prevSnake];

        // Check food collision
        if (newHead.x === food.x && newHead.y === food.y) {
          setScore(s => s + 10);
          setFood(generateFood(newSnake));
          // Increase speed slightly
          setSpeed(s => Math.max(50, s * 0.98));
        } else {
          newSnake.pop(); // Remove tail
        }

        return newSnake;
      });
    };

    const gameLoop = setInterval(moveSnake, speed);
    return () => clearInterval(gameLoop);
  }, [status, nextDirection, food, boardSize, generateFood, speed]);

  // Update High Score
  useEffect(() => {
    if (score > highScore) {
      setHighScore(score);
      localStorage.setItem('snakeHighScore', score.toString());
    }
  }, [score, highScore]);

  // Load High Score on Mount
  useEffect(() => {
    const saved = localStorage.getItem('snakeHighScore');
    if (saved) setHighScore(parseInt(saved, 10));
  }, []);

  // Handle Key Press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (status !== 'PLAYING') {
        if (e.code === 'Space' && (status === 'IDLE' || status === 'GAME_OVER')) {
          resetGame();
        }
        return;
      }

      switch (e.key) {
        case 'ArrowUp':
          if (direction !== 'DOWN') setNextDirection('UP');
          break;
        case 'ArrowDown':
          if (direction !== 'UP') setNextDirection('DOWN');
          break;
        case 'ArrowLeft':
          if (direction !== 'RIGHT') setNextDirection('LEFT');
          break;
        case 'ArrowRight':
          if (direction !== 'LEFT') setNextDirection('RIGHT');
          break;
        case ' ':
          setStatus(prev => prev === 'PLAYING' ? 'PAUSED' : 'PLAYING');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [status, direction, resetGame]);

  return {
    snake,
    food,
    status,
    score,
    highScore,
    resetGame,
    setStatus,
    boardSize
  };
}
