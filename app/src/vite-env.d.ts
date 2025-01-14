/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_GTAG_ID: string
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}