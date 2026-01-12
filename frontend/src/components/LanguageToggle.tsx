import { useLanguage } from '../contexts/LanguageContext';
import './LanguageToggle.css';

const Icons = {
  globe: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10"/>
      <line x1="2" y1="12" x2="22" y2="12"/>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    </svg>
  ),
};

export default function LanguageToggle() {
  const { language, toggleLanguage, t } = useLanguage();

  return (
    <button 
      className="language-toggle" 
      onClick={toggleLanguage}
      title={language === 'en' ? t.chatbot.changeToSpanish : t.chatbot.changeToEnglish}
      aria-label={language === 'en' ? 'Change to Spanish' : 'Cambiar a Inglés'}
    >
      <Icons.globe />
      <span className="language-code">{language.toUpperCase()}</span>
    </button>
  );
}
