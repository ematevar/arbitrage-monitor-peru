import spec from './templates/openapi.json' with { type: 'json' };
import specArgentina from './templates/openapi-argentina.json' with { type: 'json' };
import regions from '../regions.json' with { type: 'json' };
import fs from 'fs/promises';

async function init() {
    try {
        await generateOpenApi();
        await generateOperations();
        await copyRegions();
    } catch (error) {
        console.error('Error during initialization:', error);
        process.exit(1);
    }
}

/**
 * Generates OpenAPI specifications for each region by fetching exchange data
 * from the CriptoYa API and replacing placeholders in the template specs.
 */
async function generateOpenApi() {
    const errors = [];
    let successCount = 0;

    for (const region of regions) {
        try {
            const { slug, name, code } = region;
            const path = `public/${slug}`;
            await fs.mkdir(path, { recursive: true });

            // Fetch exchanges with timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

            let response;
            try {
                response = await fetch('https://criptoya.com/api/exchanges', {
                    signal: controller.signal
                });
            } finally {
                clearTimeout(timeoutId);
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const regionsByExchanges = await response.json();

            // Validate response format
            if (!regionsByExchanges || typeof regionsByExchanges !== 'object') {
                throw new Error('Invalid response format from exchanges API');
            }

            const regionExchanges = regionsByExchanges[code.toLowerCase()];

            // Skip regions with no exchanges instead of using placeholders
            if (!regionExchanges || !Array.isArray(regionExchanges) || regionExchanges.length === 0) {
                console.warn(`⚠️  No exchanges found for ${name} (${code}), skipping...`);
                continue;
            }

            // Select appropriate spec template
            const specToUse = slug === 'argentina' ? specArgentina : spec;

            // Replace placeholders with actual exchange data
            const specString = JSON.stringify(specToUse)
                .replace('"REPLACE_COTIZACION_EXCHANGE_ENUMS"',
                    regionExchanges.map(exchange => `"${exchange}"`).join(','))
                .replace('"REPLACE_COTIZACION_EXCHANGE_EXAMPLE"',
                    `"${regionExchanges[0]}"`);

            // Write generated spec to file
            await fs.writeFile(`${path}/openapi.json`,
                JSON.stringify(JSON.parse(specString), null, 4));

            console.log(`✅ Generated OpenAPI spec for ${name}`);
            successCount++;

        } catch (error) {
            const errorMsg = error.name === 'AbortError'
                ? 'Request timeout'
                : error.message;
            console.error(`❌ Failed to generate docs for ${region.name}: ${errorMsg}`);
            errors.push({ region: region.name, error: errorMsg });
            // Continue with other regions instead of failing completely
        }
    }

    // Summary report
    console.log(`\n📊 Generation Summary:`);
    console.log(`   ✅ Success: ${successCount}/${regions.length} regions`);

    if (errors.length > 0) {
        console.warn(`   ⚠️  Failed: ${errors.length} region(s)`);
        errors.forEach(({ region, error }) => {
            console.warn(`      - ${region}: ${error}`);
        });
    }
}

async function generateOperations() {
    for (const region of regions) {
        const { name, slug } = region;
        const path = `${slug}/operations`;

        await fs.mkdir(path, { recursive: true });

        const indexContent = await fs.readFile(`.vitepress/scripts/templates/index.md`, 'utf8');
        await fs.writeFile(`${slug}/index.md`, indexContent.replace('REPLACE_REGION', name));

        const operationContent = await fs.readFile(`.vitepress/scripts/templates/operations/[operationId].md`, 'utf8');
        await fs.writeFile(`${path}/[operationId].md`, operationContent.replace('REPLACE_REGION', slug));

        const pathsContent = await fs.readFile(`.vitepress/scripts/templates/operations/[operationId].paths.js`, 'utf8');
        await fs.writeFile(`${path}/[operationId].paths.js`, pathsContent.replace('REPLACE_REGION', slug));
    }
}

async function copyRegions() {
    await fs.copyFile('.vitepress/regions.json', 'public/regions.json');
}

init();
