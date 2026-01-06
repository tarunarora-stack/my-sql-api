const cors = require('cors');
const express = require('express');
const sql = require('mssql');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json()); // Allows the API to read JSON data

// Database Configuration
const dbConfig = {
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    server: process.env.DB_SERVER,
    database: process.env.DB_NAME,
    options: {
        encrypt: true, 
        trustServerCertificate: true // Necessary for local development
    }
};

// Function to handle database connection
async function connectToDb() {
    try {
        await sql.connect(dbConfig);
        console.log('Connected to MsSQL Database successfully!');
    } catch (err) {
        console.error('Database connection failed:', err);
    }
}

// ROUTE: Get all products
app.get('/products', async (req, res) => {
    try {
        const result = await sql.query`SELECT * FROM Products`;
        res.json(result.recordset);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
// ROUTE: Delete a product by ID
app.delete('/products/:id', async (req, res) => {
    try {
        const { id } = req.params; // Gets the ID from the URL (e.g., /products/3)
        const pool = await sql.connect(dbConfig);
        
        await pool.request()
            .input('Id', sql.Int, id)
            .query('DELETE FROM Products WHERE Id = @Id');

        res.json({ message: `Product with ID ${id} deleted.` });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
// ROUTE: Add a new product
app.post('/products', async (req, res) => {
    try {
        const { Name, Price } = req.body; // This pulls data from your request
        const pool = await sql.connect(dbConfig);
        
        // Using inputs protects your database from "SQL Injection" attacks
        await pool.request()
            .input('Name', sql.NVarChar, Name)
            .input('Price', sql.Decimal(10, 2), Price)
            .query('INSERT INTO Products (Name, Price) VALUES (@Name, @Price)');

        res.status(201).json({ message: 'Product added successfully!' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    connectToDb();
});