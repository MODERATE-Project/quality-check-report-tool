import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Importar los archivos de traducción directamente
import enCommon from './locales/en/common.json';
import esCommon from './locales/es/common.json';

const resources = {
  en: {
    common: enCommon
  },
  es: {
    common: esCommon
  }
};

i18n
  .use(LanguageDetector)   // detecta idioma del navegador o de localStorage
  .use(initReactI18next)   // conecta con React
  .init({
    resources,
    fallbackLng: 'es',
    supportedLngs: ['es', 'en'],
    load: 'languageOnly',
    nonExplicitSupportedLngs: true,
    ns: ['common'],
    defaultNS: 'common',
    debug: process.env.NODE_ENV === 'development',
    interpolation: { escapeValue: false },
    react: {
      useSuspense: false
    }
  });

export default i18n;
