const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp({
    storageBucket: 'rchat-3afe7.firebasestorage.app'
});

exports.cleanupTempFiles = functions.pubsub.schedule('every 1 hours').onRun(async (_context) => {
    const bucket = admin.storage().bucket();
    console.log('Starting cleanup check for files older than 24 hours...');

    try {
        const [files] = await bucket.getFiles({ prefix: 'temp/' });
        console.log(`Found ${files.length} files in temp directory`);
        
        const now = new Date();
        let deletedCount = 0;

        for (const file of files) {
            try {
                const [metadata] = await file.getMetadata();
                const fileCreatedTime = new Date(metadata.timeCreated);
                const diffInHours = (now - fileCreatedTime) / 1000 / 60 / 60;
                
                console.log(`File ${file.name} is ${diffInHours.toFixed(2)} hours old`);
                
                if (diffInHours > 24) {
                    await file.delete();
                    console.log(`Successfully deleted: ${file.name}, age: ${diffInHours.toFixed(2)} hours`);
                    deletedCount++;
                } else {
                    console.log(`Keeping file ${file.name}, not yet 24 hours old`);
                }
            } catch (error) {
                console.error(`Error processing ${file.name}:`, error);
            }
        }

        console.log(`Cleanup check completed. Found ${files.length} files, deleted ${deletedCount} files older than 24 hours`);
        return null;
    } catch (error) {
        console.error('Error during cleanup:', error);
        throw error;
    }
});