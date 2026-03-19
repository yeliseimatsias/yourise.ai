export const mockApiResponse = [
  {
    text: "Статья 1. Основные положения",
    type: "unchanged",
    risk: null,
    recommendation: null,
    article: null
  },
  {
    text: "1. Настоящий Закон регулирует отношения в области экспериментального права и инноваций.",
    type: "unchanged",
    risk: null,
    recommendation: null,
    article: null
  },
  {
    text: "2. Действие настоящего Закона распространяется на всех участников эксперимента, включая иностранных лиц.",
    type: "unchanged",
    risk: null,
    recommendation: null,
    article: null
  },
  {
    text: "",
    type: "unchanged",
    risk: null,
    recommendation: null,
    article: null
  },
  {
    text: "Статья 2. Права и обязанности",
    type: "unchanged",
    risk: null,
    recommendation: null,
    article: null
  },
  {
    text: "1. Участники имеют право на получение полной и достоверной информации.",
    type: "modified",
    risk: "green",
    recommendation: "Стилистическое изменение, безопасно.",
    article: null
  },
  {
    text: "2. Участники обязаны соблюдать условия эксперимента и предоставлять отчеты.",
    type: "modified",
    risk: "yellow",
    recommendation: "Добавлена обязанность отчётности, проверьте форму отчёта.",
    article: null
  },
  {
    text: "3. За нарушение предусмотрена административная ответственность.",
    type: "modified",
    risk: "red",
    recommendation: "Изменение вида ответственности требует согласования с административным кодексом.",
    article: {
      id: "2",
      title: "Статья 2",
      url: "/law/article/2"
    }
  },
  {
    text: "4. Участники имеют право на обжалование решений.",
    type: "added",
    risk: "green",
    recommendation: "Новое право, соответствует общим принципам.",
    article: null
  }
];