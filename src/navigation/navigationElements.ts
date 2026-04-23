import {
  mapViewNavigationData,
  settingsViewNavigationData,
  aboutViewNavigationData,
  analyticsViewNavigationData,
} from "../views/viewKeys.ts";

import type { INavigationElement } from "./navigationTypes.js";

export const navigationElements: Array<INavigationElement> = [
  aboutViewNavigationData,
  settingsViewNavigationData,
  mapViewNavigationData,
  analyticsViewNavigationData,
];

export const getImportableView = async (dynamicFilePath: string) => {
  let page: any;

  if (dynamicFilePath === "views/MapView") {
    page = await import("./../views/MapView.tsx");
  }
  if (dynamicFilePath === "views/SettingsView") {
    page = await import("./../views/SettingsView.tsx");
  }
  if (dynamicFilePath === "views/AboutView") {
    page = await import("./../views/AboutView.tsx");
  }
  if (dynamicFilePath === "views/AnalyticsView") {
    page = await import("./../views/AnalyticsView.tsx");
  }
  return page;
};
