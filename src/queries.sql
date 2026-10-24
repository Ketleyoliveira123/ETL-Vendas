SELECT COUNT(*) AS total_vendas
FROM vendas;

SELECT SUM(quantidade  * prec_unitario) AS fasturamento_total
FROM vendas;

SELECT 
    cidade, 
    ROUND(SUM(quantidade * prec_unitario), 2) AS faturamento_total
FROM vendas
GROUP BY cidade
ORDER BY faturamento_total DESC;

SELECT
    nome_produto,
    CAST(SUM(quantidade) AS INTEGER) AS total_vendido
FROM vendas
GROUP BY nome_produto
ORDER BY total_vendido DESC;