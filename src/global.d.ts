declare module '*.jpg';
declare module '*.png';
declare module '*.jpeg';
declare module '*.svg';
declare module '*.mp4';

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
