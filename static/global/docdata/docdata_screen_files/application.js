/*
 * This is a server hosted configuration file for the GWT client application.
 * All clients share this same configuration, it's read upon client startup/load.
 * Note that since this is loaded/used client side, it is public by definition.
 * 
 * This enables administrators to change these settings for the application
 * while it is deployed.
 * 
 * Other settings are sent from the server using the same kind of structure,
 * but they are rendered dynamically inside the host page.
 */
var ApplicationSettings = {
    menuInteractionSubmitIntervalSeconds: "3",
    statusTriesMaxAttempts: "5",
    statusTriesSleepMillis: "5000"
};
