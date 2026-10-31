import {registerCatalog} from './catalog.js';
import {registerPreferences} from './preferences.js';
import {registerNotifications} from './notifications.js';
import {registerFiles} from './files.js';
import {registerSystem} from './system.js';
import {registerApplicationActions} from './application-actions.js';
export function registerServices(host) {
  registerCatalog(host); registerPreferences(host); registerNotifications(host);
  registerFiles(host); registerSystem(host); registerApplicationActions(host);
}
