# Tugas Besar Kelompok 5 Big Data

## API
### Cara Penggunaan
1. Run this for the first time:
```
docker-compose up --build
```
or
```
docker-compose up -d --build
docker-compose logs -f api
```
for detached mode

2. For the second time just run
```
docker-compose up
```
or
```
docker-compose up -d
docker-compose logs -f api
```
for detached mode

3. API should be accessable in localhost:5000

# API Documentations

## General Notes

*   **Emiten Parameter (`<emiten>`)**: This parameter represents the stock ticker symbol.
    *   For **Stock Data** (`/api/stock/<emiten>`), the `emiten` should match the exact symbol stored in the database (e.g., `AALI.JK`).
    *   For **News Data** (`/api/news/<emiten>`), **News Summary** (`/api/news/summary/<emiten>`), and **Financial Reports** (`/api/financial/<emiten>`), you can provide the `emiten` with or without the `.JK` suffix (e.g., `AALI` or `AALI.JK`). The API will handle it appropriately. The response will generally include the `.JK` suffix.
*   **Error Handling**: The API returns standard HTTP status codes for errors. Common errors include `400 Bad Request` for invalid parameters, `404 Not Found` for non-existent resources or data, and `500 Internal Server Error` for server-side issues. Error responses are in JSON format with an "error" or "message" key.

## Endpoints

### 1. Get Stock Data

Fetches historical stock data for a given emiten, with options for data aggregation period.

*   **Endpoint**: `GET /api/stock/<emiten>`
*   **Path Parameter**:
    *   `emiten` (string, required): The stock ticker symbol (e.g., `AALI.JK`).
*   **Query Parameter**:
    *   `period` (string, optional, default: `all`): Specifies the aggregation period for the stock data.
        *   Valid values:
            *   `3days`: Data for the last 3 days
            *   `1week`: Data for the last 1 week
            *   `1month`: Data for the last 1 month
            *   `3month`: Data for the last 3 month
            *   `1y`: Data for the last 1 year (daily granularity unless combined with other aggregation).
            *   `3y`: Data for the last 3 years.
            *   `5y`: Data for the last 5 years.
            *   `all`: All available historical data (daily granularity).
*   **Success Response (200 OK)**:
    *   A JSON array of stock data objects. Each object typically includes `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, and `emiten`.
*   **Error Responses**:
    *   `400 Bad Request`: If an invalid `period` is specified.
    *   `404 Not Found`: If no data is found for the given `emiten` and `period`.
    *   `500 Internal Server Error`: If there's an issue fetching or processing data.
*   **Example**:
    *   `GET /api/stock/AALI.JK?period=monthly`
    *   `GET /api/stock/BBCA.JK?period=1y`

### 2. Get News Data

Fetches news articles related to a specific emiten. Supports pagination.

*   **Endpoint**: `GET /api/news/<emiten>`
*   **Path Parameter**:
    *   `emiten` (string, required): The stock ticker symbol (e.g., `AALI` or `AALI.JK`).
*   **Query Parameters**:
    *   `limit` (integer, optional, default: `20`): The maximum number of news articles to return per request. This controls the "page size".
    *   `skip` (integer, optional, default: `0`): The number of news articles to skip from the beginning of the dataset. This is used for pagination. For example, to get the second page of 20 articles, you would use `limit=20` and `skip=20`.
*   **Success Response (200 OK)**:
    *   A JSON array of news article objects. The structure of these objects depends on your database schema but will include an `Emiten` field with the `.JK` suffix.
*   **Example**:
    *   `GET /api/news/AALI?limit=10&skip=0` (gets the first 10 news articles for AALI)
    *   `GET /api/news/BBCA.JK?limit=5&skip=5` (gets news articles 6 through 10 for BBCA.JK)

### 3. Get News Summary Data

Fetches summarized news articles related to a specific emiten. Supports pagination.

*   **Endpoint**: `GET /api/news/summary/<emiten>`
*   **Path Parameter**:
    *   `emiten` (string, required): The stock ticker symbol (e.g., `AALI` or `AALI.JK`).
*   **Query Parameters**:
    *   `limit` (integer, optional, default: `20`): The maximum number of news summaries to return per request.
    *   `skip` (integer, optional, default: `0`): The number of news summaries to skip from the beginning.
*   **Success Response (200 OK)**:
    *   A JSON array of news summary objects. The structure depends on your database schema but will include an `Emiten` field with the `.JK` suffix.
*   **Example**:
    *   `GET /api/news/summary/TLKM?limit=5` (gets the first 5 news summaries for TLKM)
    *   `GET /api/news/summary/ASII.JK?limit=10&skip=20` (gets news summaries 21 through 30 for ASII.JK)

### 4. Get Financial Report Data

Fetches financial report data for a specific emiten. It can retrieve the report for a specific year or the latest available report if no year is specified.

*   **Endpoint**: `GET /api/financial/<emiten>`
*   **Path Parameter**:
    *   `emiten` (string, required): The stock ticker symbol (e.g., `AALI` or `AALI.JK`).
*   **Query Parameter**:
    *   `year` (string, optional): The year of the financial report to retrieve (e.g., `2023`).
        *   Valid values: `2021`, `2022`, `2023`, `2024`, `2025`.
        *   If this parameter is omitted, the API will return the most recent financial report available for the emiten.
*   **Success Response (200 OK)**:
    *   A JSON object containing the financial report data. The structure depends on your database schema but will include an `EntityCode` field with the `.JK` suffix.
*   **Error Responses**:
    *   `400 Bad Request`: If an invalid `year` is specified.
    *   `404 Not Found`: If no report is found for the given `emiten` and `year`.
*   **Example**:
    *   `GET /api/financial/GOTO` (gets the latest report)
    *   `GET /api/financial/BMRI.JK?year=2023` (gets the report for the year 2023)

## (`limit` and `skip`) parameters on news data

The `limit` and `skip` query parameters are used together to implement pagination for endpoints that can return a large number of items (like news articles or summaries).

*   **`limit`**: Determines the maximum number of items to be returned in a single API call. Think of this as the "page size".
*   **`skip`**: Determines how many items to bypass from the beginning of the full dataset before starting to collect the items to return. Think of this as the "offset".

**How it works:**

*   To get the **first page** of items: `limit=N&skip=0` (returns items 1 to N)
*   To get the **second page** of items: `limit=N&skip=N` (returns items N+1 to 2N)
*   To get the **third page** of items: `limit=N&skip=2N` (returns items 2N+1 to 3N)
*   And so on... In general, for page `P` (1-indexed) with `N` items per page: `limit=N&skip=(P-1)*N`.

**Example:**
If you want to display news articles in pages of 10:
*   Page 1: `GET /api/news/AALI?limit=10&skip=0`
*   Page 2: `GET /api/news/AALI?limit=10&skip=10`
*   Page 3: `GET /api/news/AALI?limit=10&skip=20`
