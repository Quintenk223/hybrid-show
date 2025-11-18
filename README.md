# Hytraq - Hybrid Tracking Website

A modern, responsive landing page for Hytraq, a hybrid GPS + NFC tracking solution for temporary and flexible asset tracking.

## 🚀 Features

- **Responsive Design**: Fully responsive layout that works on all devices
- **Smooth Scrolling**: Enhanced navigation with smooth scroll behavior
- **Form Validation**: Client-side form validation with user feedback
- **Modern UI**: Clean, professional design with hover effects and transitions
- **Accessibility**: Semantic HTML and ARIA labels for better accessibility

## 📁 Project Structure

```
hybrid-site/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # Main stylesheet
├── js/
│   └── main.js         # JavaScript functionality
├── images/             # Image assets (add your images here)
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## 🛠️ Setup

1. Clone or download this repository
2. Open `index.html` in a web browser
3. For development, use a local server (recommended):
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js (http-server)
   npx http-server
   ```

## 📝 Customization

### Images

Replace placeholder images in the `images/` directory:
- `hero-image.jpg` - Hero section image
- `gps-tracking.jpg` - GPS tracking section image
- `product-detail.jpg` - Product detail section image

The HTML includes fallback placeholder images if local images are not found.

### Form Submission

The contact form currently uses client-side validation only. To enable actual form submission:

1. **Option 1: Use a form service** (e.g., Formspree, Netlify Forms)
   - Sign up for a service
   - Update the form action in `index.html`
   - Configure the service endpoint

2. **Option 2: Backend integration**
   - Update `js/main.js` to send form data to your API
   - Replace the setTimeout simulation with actual fetch/axios call

### Styling

All styles are in `css/styles.css`. The color scheme uses:
- Primary: `#0a0f2c` (dark blue)
- Background: `#f5f6fa` (light gray)
- Text: `#222` (dark gray)

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📱 Responsive Breakpoints

- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px
- Small Mobile: < 480px

## 🔧 Development

### Adding New Sections

1. Add HTML section in `index.html`
2. Add corresponding styles in `css/styles.css`
3. Update navigation if needed

### JavaScript Features

- Smooth scrolling for anchor links
- Form validation and submission handling
- Active navigation highlighting on scroll

## 📄 License

This project is proprietary. All rights reserved.

## 🤝 Contributing

This is a private project. For changes or improvements, please contact the project maintainer.

## 📧 Contact

For demo requests or inquiries, use the contact form on the website.

---

**Note**: This is a static website. For production deployment, consider:
- Adding a build process (if needed)
- Setting up proper form handling
- Implementing analytics
- Adding SEO meta tags
- Setting up a CDN for assets


