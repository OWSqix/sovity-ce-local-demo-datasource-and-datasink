// frontend/src/environments/environment.ts

export const environment = {
  production: false,
  dataSourceApiUrl: '${DATA_SOURCE_API_URL}',  // 환경 변수로 대체될 템플릿 변수
  dataSinkApiUrl: '${DATA_SINK_API_URL}'       // 환경 변수로 대체될 템플릿 변수
};
