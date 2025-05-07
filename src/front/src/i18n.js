import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import resources from 'virtual:i18next-loader'; // lo inyecta el plugin de Vite

i18n
  .use(LanguageDetector)   // detecta idioma del navegador o de localStorage
  .use(initReactI18next)   // conecta con React
  .init({
    resources,
    fallbackLng: 'es',
    supportedLngs: ['es', 'en'],
    nonExplicitSupportedLngs: true,
    ns: ['common', 'home'],
    defaultNS: 'common',
    debug: import.meta.env.DEV,
    interpolation: { escapeValue: false }
  });

export default i18n;
