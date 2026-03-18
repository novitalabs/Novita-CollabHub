// Snake Game Core Logic

class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.tileCount = 20;
        
        // Game state
        this.snake = [];
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        this.food = { x: 0, y: 0 };
        this.score = 0;
        this.highScore = this.loadHighScore();
        this.isGameOver = false;
        this.isPlaying = false;
        this.isPaused = false;
        this.gameSpeed = 100;
        this.gameLoop = null;
        
        // Initialize
        this.initElements();
        this.setupEventListeners();
        this.updateHighScoreDisplay();
    }
    
    initElements() {
        this.scoreElement = document.getElementById('score');
        this.highScoreElement = document.getElementById('highScore');
        this.finalScoreElement = document.getElementById('finalScore');
        this.gameOverScreen = document.getElementById('gameOver');
        this.gameStartScreen = document.getElementById('gameStart');
        this.startBtn = document.getElementById('startBtn');
        this.restartBtn = document.getElementById('restartBtn');
        this.speedSelect = document.getElementById('speedSelect');
    }
    
    setupEventListeners() {
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // Button events
        this.startBtn.addEventListener('click', () => this.startGame());
        this.restartBtn.addEventListener('click', () => this.restartGame());
        
        // Speed selection
        this.speedSelect.addEventListener('change', (e) => {
            this.gameSpeed = parseInt(e.target.value);
        });
        
        // Mobile control buttons
        const controlButtons = document.querySelectorAll('.btn-control');
        controlButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const direction = btn.dataset.direction;
                this.handleMobileControl(direction);
            });
        });
        
        // Touch swipe controls
        let touchStartX = 0;
        let touchStartY = 0;
        
        this.canvas.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });
        
        this.canvas.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                // Horizontal swipe
                if (deltaX > 30 && this.direction.x !== -1) {
                    this.nextDirection = { x: 1, y: 0 };
                } else if (deltaX < -30 && this.direction.x !== 1) {
                    this.nextDirection = { x: -1, y: 0 };
                }
            } else {
                // Vertical swipe
                if (deltaY > 30 && this.direction.y !== -1) {
                    this.nextDirection = { x: 0, y: 1 };
                } else if (deltaY < -30 && this.direction.y !== 1) {
                    this.nextDirection = { x: 0, y: -1 };
                }
            }
        });
    }
    
    handleKeyPress(e) {
        if (!this.isPlaying) return;
        
        // Space key to pause
        if (e.code === 'Space') {
            e.preventDefault();
            this.togglePause();
            return;
        }
        
        if (this.isPaused) return;
        
        // Arrow key controls
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                if (this.direction.y !== 1) {
                    this.nextDirection = { x: 0, y: -1 };
                }
                break;
            case 'ArrowDown':
                e.preventDefault();
                if (this.direction.y !== -1) {
                    this.nextDirection = { x: 0, y: 1 };
                }
                break;
            case 'ArrowLeft':
                e.preventDefault();
                if (this.direction.x !== 1) {
                    this.nextDirection = { x: -1, y: 0 };
                }
                break;
            case 'ArrowRight':
                e.preventDefault();
                if (this.direction.x !== -1) {
                    this.nextDirection = { x: 1, y: 0 };
                }
                break;
        }
    }
    
    handleMobileControl(direction) {
        if (!this.isPlaying || this.isPaused) return;
        
        switch (direction) {
            case 'up':
                if (this.direction.y !== 1) {
                    this.nextDirection = { x: 0, y: -1 };
                }
                break;
            case 'down':
                if (this.direction.y !== -1) {
                    this.nextDirection = { x: 0, y: 1 };
                }
                break;
            case 'left':
                if (this.direction.x !== 1) {
                    this.nextDirection = { x: -1, y: 0 };
                }
                break;
            case 'right':
                if (this.direction.x !== -1) {
                    this.nextDirection = { x: 1, y: 0 };
                }
                break;
        }
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
        if (!this.isPaused) {
            this.run();
        }
    }
    
    startGame() {
        this.gameStartScreen.classList.add('hidden');
        this.isPlaying = true;
        this.resetGame();
        this.run();
    }
    
    restartGame() {
        this.gameOverScreen.classList.remove('show');
        this.isPlaying = true;
        this.resetGame();
        this.run();
    }
    
    resetGame() {
        // Reset snake position (start from center)
        const centerX = Math.floor(this.tileCount / 2);
        const centerY = Math.floor(this.tileCount / 2);
        
        this.snake = [
            { x: centerX, y: centerY },
            { x: centerX - 1, y: centerY },
            { x: centerX - 2, y: centerY }
        ];
        
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        this.score = 0;
        this.isGameOver = false;
        this.isPaused = false;
        
        this.updateScore();
        this.spawnFood();
    }
    
    spawnFood() {
        let newFood;
        let isOnSnake;
        
        do {
            isOnSnake = false;
            newFood = {
                x: Math.floor(Math.random() * this.tileCount),
                y: Math.floor(Math.random() * this.tileCount)
            };
            
            // Ensure food doesn't spawn on the snake
            for (let segment of this.snake) {
                if (segment.x === newFood.x && segment.y === newFood.y) {
                    isOnSnake = true;
                    break;
                }
            }
        } while (isOnSnake);
        
        this.food = newFood;
    }
    
    run() {
        if (this.gameLoop) {
            clearTimeout(this.gameLoop);
        }
        
        if (!this.isGameOver && !this.isPaused) {
            this.update();
            this.draw();
            this.gameLoop = setTimeout(() => this.run(), this.gameSpeed);
        }
    }
    
    update() {
        // Update direction
        this.direction = { ...this.nextDirection };
        
        // Calculate new head position
        const head = { ...this.snake[0] };
        head.x += this.direction.x;
        head.y += this.direction.y;
        
        // Check collision
        if (this.checkCollision(head)) {
            this.endGame();
            return;
        }
        
        // Add new head
        this.snake.unshift(head);
        
        // Check if food is eaten
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            this.updateScore();
            this.spawnFood();
            // Play sound effect
            this.playSound(200, 0.1);
        } else {
            // Remove tail
            this.snake.pop();
        }
    }
    
    checkCollision(head) {
        // Check wall collision
        if (head.x < 0 || head.x >= this.tileCount || 
            head.y < 0 || head.y >= this.tileCount) {
            return true;
        }
        
        // Check self collision
        for (let i = 0; i < this.snake.length; i++) {
            if (this.snake[i].x === head.x && this.snake[i].y === head.y) {
                return true;
            }
        }
        
        return false;
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
        
        // Draw food
        this.drawFood();
        
        // Draw snake
        this.drawSnake();
        
        // If paused, show pause text
        if (this.isPaused) {
            this.drawPausedText();
        }
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#0a0a0a';
        this.ctx.lineWidth = 1;
        
        for (let i = 0; i <= this.tileCount; i++) {
            // Vertical lines
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.gridSize, 0);
            this.ctx.lineTo(i * this.gridSize, this.canvas.height);
            this.ctx.stroke();
            
            // Horizontal lines
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.gridSize);
            this.ctx.lineTo(this.canvas.width, i * this.gridSize);
            this.ctx.stroke();
        }
    }
    
    drawSnake() {
        this.snake.forEach((segment, index) => {
            // Different color for head
            if (index === 0) {
                this.ctx.fillStyle = '#ffff00';
                this.ctx.shadowBlur = 10;
                this.ctx.shadowColor = '#ffff00';
            } else {
                this.ctx.fillStyle = '#00ff41';
                this.ctx.shadowBlur = 5;
                this.ctx.shadowColor = '#00ff41';
            }
            
            const x = segment.x * this.gridSize;
            const y = segment.y * this.gridSize;
            
            // Draw bordered block
            this.ctx.fillRect(x + 1, y + 1, this.gridSize - 2, this.gridSize - 2);
            
            // Add pixel effect
            this.ctx.strokeStyle = index === 0 ? '#cccc00' : '#00cc33';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(x + 1, y + 1, this.gridSize - 2, this.gridSize - 2);
        });
        
        // Reset shadow
        this.ctx.shadowBlur = 0;
    }
    
    drawFood() {
        this.ctx.fillStyle = '#ff0040';
        this.ctx.shadowBlur = 15;
        this.ctx.shadowColor = '#ff0040';
        
        const x = this.food.x * this.gridSize;
        const y = this.food.y * this.gridSize;
        
        // Draw pulsing food
        const pulse = Math.sin(Date.now() / 200) * 0.2 + 0.8;
        const size = this.gridSize * pulse;
        const offset = (this.gridSize - size) / 2;
        
        this.ctx.fillRect(x + offset, y + offset, size, size);
        
        // Reset shadow
        this.ctx.shadowBlur = 0;
    }
    
    drawPausedText() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#ffff00';
        this.ctx.font = '20px "Press Start 2P"';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        const text = 'PAUSED';
        this.ctx.fillText(text, this.canvas.width / 2, this.canvas.height / 2);
    }
    
    updateScore() {
        this.scoreElement.textContent = this.score;
    }
    
    updateHighScoreDisplay() {
        this.highScoreElement.textContent = this.highScore;
    }
    
    endGame() {
        this.isGameOver = true;
        this.isPlaying = false;
        
        // Update high score
        if (this.score > this.highScore) {
            this.highScore = this.score;
            this.saveHighScore();
            this.updateHighScoreDisplay();
        }
        
        // Show game over screen
        this.finalScoreElement.textContent = this.score;
        this.gameOverScreen.classList.add('show');
        
        // Play game over sound
        this.playSound(100, 0.2);
    }
    
    playSound(frequency, duration) {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'square';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        } catch (e) {
            // Silently handle audio playback failure
        }
    }
    
    saveHighScore() {
        localStorage.setItem('snakeHighScore', this.highScore.toString());
    }
    
    loadHighScore() {
        const saved = localStorage.getItem('snakeHighScore');
        return saved ? parseInt(saved) : 0;
    }
}

// Initialize game
document.addEventListener('DOMContentLoaded', () => {
    const game = new SnakeGame();
});