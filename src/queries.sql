-- Total de vendas
SELECT COUNT(*) AS total_vendas
FROM vendas;

-- Faturamento total
SELECT ROUND(SUM(quantidade * preco_unitario), 2) AS faturamento_total
FROM vendas;

-- Faturamento por cidade
SELECT
    cidade,
    ROUND(SUM(quantidade * preco_unitario), 2) AS faturamento_total
FROM vendas
GROUP BY cidade
ORDER BY faturamento_total DESC;

-- Produtos mais vendidos
SELECT
    nome_produto,
    CAST(SUM(quantidade) AS INTEGER) AS total_vendido
FROM vendas
GROUP BY nome_produto
ORDER BY total_vendido DESC;
