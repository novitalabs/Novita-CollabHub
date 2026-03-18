# 🐍 Retro Snake Game

A classic Snake game with retro visual style, built with pure HTML, CSS, and JavaScript.

## 🎮 Features

- **Retro Pixel Style**: Classic pixel art style with retro color scheme
- **Neon Glow Effect**: Green neon theme with glowing shadow effects
- **Smooth Gameplay**: 60fps smooth animation with responsive controls
- **Multiple Controls**: Supports keyboard, touch swipe, and mobile button controls
- **Adjustable Difficulty**: Choose from Slow, Medium, Fast, and Extreme speeds
- **Local Storage**: Automatically saves high score
- **Sound Effects**: Retro-style 8-bit sound effects

## 🕹️ How to Play

### Desktop Controls
- **Arrow Keys (↑↓←→)**: Control the snake's direction
- **Space**: Pause/Resume the game

### Mobile Controls
- **Touch Swipe**: Swipe on the game canvas to control the snake
- **Direction Buttons**: Use the on-screen direction buttons

### Game Rules
1. Control the snake to eat red food to grow longer
2. Each food item scores 10 points
3. Don't hit the walls or bite your own body
4. Try to get the highest score!

## 🎨 Visual Design

- **Color Scheme**:
  - Background: Dark blue gradient (#0f0f23 to #1a1a3e)
  - Snake body: Neon green (#00ff41)
  - Snake head: Neon yellow (#ffff00)
  - Food: Neon red (#ff0040)
  
- **Font**: Press Start 2P (classic pixel font)
- **Effects**: Glow shadows, border animations, pulse effects

## 📁 Project Structure

```
/
├── index.html          # Main page
├── css/
│   └── style.css      # Retro style stylesheet
├── js/
│   └── game.js        # Game core logic
└── README.md          # Project documentation
```

## 🚀 Completed Features

### Core Game
- ✅ Snake movement and direction control
- ✅ Food generation and collision detection
- ✅ Wall and self-collision detection
- ✅ Scoring system
- ✅ Game over detection

### User Interface
- ✅ Game start screen
- ✅ Game over screen
- ✅ Real-time score display
- ✅ High score display
- ✅ Pause functionality

### Control System
- ✅ Keyboard arrow key controls
- ✅ Mobile touch swipe controls
- ✅ Mobile direction button controls
- ✅ Pause/Resume (Space key)

### Visual Effects
- ✅ Retro pixel style design
- ✅ Neon glow effects
- ✅ Grid background
- ✅ Animations (border glow, food pulse, button interactions)
- ✅ Responsive layout

### Game Settings
- ✅ Adjustable game speed (Slow/Medium/Fast/Extreme)
- ✅ Local storage for high score
- ✅ 8-bit sound effects

## 🎯 Entry Points

- **Home**: `index.html` - Main game interface with all features
  - Start game button
  - Score and high score display
  - Game canvas (400x400 pixels, 20x20 grid)
  - Control instructions
  - Speed settings

## 💡 Technical Implementation

### Game Architecture
- **Object-Oriented Design**: Game logic encapsulated using ES6 classes
- **Canvas Rendering**: Game visuals drawn using HTML5 Canvas API
- **Event-Driven**: Keyboard, touch, and click event handling
- **Timed Loop**: Game loop implemented using setTimeout

### Key Technical Details
- **Collision Detection**: Detects collisions between snake and walls, self, and food
- **Direction Control**: Logic to prevent 180° turns
- **Random Generation**: Ensures food doesn't spawn on the snake
- **Local Storage**: Uses localStorage to save high scores
- **Web Audio API**: Generates retro-style sound effects

## 🔧 Future Improvements

1. **Game Modes**
   - Add wall-less mode (wrap-around)
   - Add obstacle challenge mode
   - Add timed mode

2. **Enhanced Features**
   - Add more sound effects and background music
   - Add leaderboard system
   - Add achievement system
   - Add skin/theme switching

3. **User Experience**
   - Add game tutorial
   - Add difficulty selection screen
   - Optimize mobile experience
   - Add fullscreen mode

4. **Visual Effects**
   - Add particle effects
   - Add more animation transitions
   - Add snake trail effects

## 🌐 Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera
- Mobile browsers

## 📝 Development Notes

This is a pure static web application that requires no server-side support. Simply open the `index.html` file in a browser to run.

### Running Locally
1. Download the project files
2. Open `index.html` in a browser
3. Click the "Start Game" button to begin playing

### Customization
You can adjust the game by modifying configuration parameters in `js/game.js`:
- `gridSize`: Grid size (default 20 pixels)
- `tileCount`: Grid count (default 20x20)
- `gameSpeed`: Game speed (default 100ms)

## 🎉 Enjoy the Game!

Have fun with this classic retro-style Snake game and challenge your high score!
