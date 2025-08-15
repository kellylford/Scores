# Sports Scores Web App

A web-based sports scores application that follows the same navigation structure as the Windows desktop version. Get live scores, standings, and game details for MLB, NFL, NBA, and NHL.

## Features

- **Same Navigation as Windows App**: Home (league selection) → League (scores + date nav) → Game Details
- **Accessible Design**: Full keyboard navigation, ARIA labels, and screen reader support
- **Native HTML Controls**: Built with semantic HTML and progressive enhancement
- **Responsive Layout**: Works on desktop and mobile devices
- **Local Hosting**: Can be hosted locally without any server requirements

## Navigation Structure

### 1. Home View - League Selection
- Select from MLB, NFL, NBA, or NHL
- Use arrow keys to navigate, Enter to select

### 2. League View - Scores & Date Navigation  
- View games for selected league and date
- Navigate dates with Previous/Next buttons or arrow keys
- Access news and standings via special menu items
- Keyboard shortcuts: 
  - Arrow keys: Navigate games list
  - Enter/Space: View game details
  - Escape: Return to league selection

### 3. Game Details View
- Detailed information about selected game
- Sport-specific data (innings for baseball, drives for football)
- Keyboard navigation through details
- Escape: Return to scores list

## Accessibility Features

- **Keyboard Navigation**: Full app navigation without mouse
  - Arrow keys: Navigate lists
  - Home/End: Jump to first/last item
  - Enter/Space: Activate selection
  - Escape: Go back/close modals

- **Screen Reader Support**: 
  - ARIA labels and roles
  - Live regions for dynamic content
  - Proper heading structure
  - Skip-to-content link

- **Visual Accessibility**:
  - High contrast mode support
  - Reduced motion support
  - Focus indicators
  - Large clickable areas

## Local Hosting

### Option 1: Python HTTP Server
```bash
# Navigate to the web app directory
cd /path/to/sports-scores-webapp

# Start local server (Python 3)
python -m http.server 8000

# Or Python 2
python -m SimpleHTTPServer 8000

# Open browser to http://localhost:8000
```

### Option 2: Node.js HTTP Server
```bash
# Install global server (if not already installed)
npm install -g http-server

# Start server
http-server -p 8000

# Open browser to http://localhost:8000
```

### Option 3: PHP Built-in Server
```bash
# Start PHP server
php -S localhost:8000

# Open browser to http://localhost:8000
```

### Option 4: Any Web Server
Simply place the files in any web server directory and access via browser.

## Files Structure

```
sports-scores-webapp/
├── index.html          # Main HTML file
├── app.js              # Main application logic
├── api.js              # ESPN API integration
├── styles.css          # Styling and responsive design
└── WEBAPP_README.md    # This file
```

## Browser Requirements

- Modern browser with ES6+ support (Chrome 61+, Firefox 55+, Safari 11+, Edge 79+)
- JavaScript enabled
- Internet connection for live data (fallback behavior when offline)

## API Data Source

Data is provided by ESPN's public API. The app includes error handling for:
- Network connectivity issues
- API rate limiting
- CORS restrictions (when hosting locally)
- Data format changes

## Keyboard Shortcuts Summary

| Key | Action |
|-----|--------|
| Arrow Keys | Navigate lists |
| Home | Jump to first item |
| End | Jump to last item |
| Enter/Space | Select item |
| Escape | Go back/close modal |
| Tab | Standard web navigation |

## Development Notes

The web app mirrors the Windows desktop application's:
- Navigation flow and structure
- Keyboard accessibility patterns
- Visual design principles
- User interaction model

This ensures a consistent experience across platforms while leveraging web technologies for broader accessibility.

## Troubleshooting

### CORS Issues
When hosting locally, you may encounter CORS errors accessing ESPN's API. This is normal and expected. The app includes fallback behavior and error handling.

### No Data Loading
- Ensure internet connection
- Check browser console for errors
- Try refreshing the page
- Verify local server is running correctly

### Keyboard Navigation Not Working
- Ensure JavaScript is enabled
- Click on the page to establish focus
- Try refreshing the page

## Browser Support

Tested and supported in:
- ✅ Chrome 90+
- ✅ Firefox 85+  
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

This web app is designed to maintain feature parity with the Windows desktop application. Any changes should preserve:
- Accessibility features
- Keyboard navigation patterns
- Visual consistency
- Local hosting capability