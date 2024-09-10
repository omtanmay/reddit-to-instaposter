const { IgApiClient } = require('instagram-private-api');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);

// Instagram credentials
const instagram_username = "YOUR IG USERNAME";
const instagram_password = "YOUR IG PASSWORD";

// Directory where images are saved
const imagesDirectory = path.join(__dirname, 'Images'); // Adjust path as necessary

// Function to get the latest image file
async function getLatestImageFile() {
    const files = await readdir(imagesDirectory);
    const imageFiles = files.filter(file => file.endsWith('.jpg') || file.endsWith('.jpeg'));

    if (imageFiles.length === 0) {
        throw new Error('No image files found.');
    }

    // Get the latest file
    const latestFile = await imageFiles.reduce(async (latest, file) => {
        const filePath = path.join(imagesDirectory, file);
        const fileStat = await stat(filePath);
        if (!latest || fileStat.mtime > latest.mtime) {
            return { file: filePath, mtime: fileStat.mtime };
        }
        return latest;
    }, null);

    return latestFile.file;
}

(async () => {
    try {
        // Get the latest image file
        const imageFilePath = await getLatestImageFile();
        console.log('Using image file:', imageFilePath);

        // Instagram client setup
        const ig = new IgApiClient();
        ig.state.generateDevice(instagram_username);

        // Log in
        await ig.account.login(instagram_username, instagram_password);
        console.log('Logged in successfully.');

        // Read captions
        const captionFilePath = path.join(__dirname, 'Memory', 'Caption.txt');
        const caption2FilePath = path.join(__dirname, 'Memory', 'Caption2.txt');
        const text = fs.readFileSync(captionFilePath, 'utf8');
        const text2 = fs.readFileSync(caption2FilePath, 'utf8');
        const caption = text + text2;

        // Upload photo
        const photo = await ig.publish.photo({
            file: fs.readFileSync(imageFilePath),
            caption: caption
        });
        console.log("Photo posted successfully:", photo);

    } catch (err) {
        console.error('Failed to upload:', err);
    }
})();
