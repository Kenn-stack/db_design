--Break down total transactions, confirmation rates, and average network fees by blockchain.
select 
	blockchain,
	COUNT(*) as total_transactions,
	ROUND((COUNT(*) FILTER (WHERE t.status = 'CONFIRMED')::NUMERIC / COUNT(*)) * 100, 2) as confirmation_rate,
	ROUND(AVG(t.fee)::NUMERIC, 2) as average_fee
from wallet_addresses w
left join transactions t
	on w.id = t.sender_wallet
group by blockchain



--Aggregate transaction metrics per wallet and blockchain address
--These will be the metrics that I'll be calculating
--*Total number of transactions
--*Total amount sent
--*Average transaction size
--*Last transaction date

select 
	w.wallet_name,
	wa.public_address,
	wa.blockchain,
	COUNT(*) as total_transactions,
	SUM(t.amount)::numeric as total_amount_sent,
	AVG(t.amount)::numeric as avg_transaction_size,
	MAX(t.timestamp) as last_transaction_date,
	
from transactions t
left join wallet_addresses wa 
	on t.sender_wallet = wa.id 
left join wallets w
	on w.id = wa.wallet_id 
group by wallet_name, public_address, blockchain
order by w.wallet_name 
	
	

--Daily transaction volume, 7-day moving average, and running totals
WITH daily_wallet_metrics AS (
    -- Step 1: Aggregate transactions into daily totals per wallet and blockchain
    SELECT 
        wa.blockchain,
        wa.public_address AS wallet_address,
        DATE_TRUNC('day', t.timestamp) AS tx_date,
        SUM(t.amount) AS daily_volume
    FROM transactions t
    JOIN wallet_addresses wa ON t.sender_wallet  = wa.id
    GROUP BY 
        wa.blockchain,
        wa.public_address,
        DATE_TRUNC('day', t.timestamp)
)
-- Step 2: Apply window functions on top of the daily aggregated metrics
SELECT 
    blockchain,
    wallet_address,
    tx_date::DATE AS date,
    
    -- 1. Daily Transaction Volume
    daily_volume,
    
    -- 2. Cumulative Running Total per wallet address over time
    SUM(daily_volume) OVER (
        PARTITION BY blockchain, wallet_address 
        ORDER BY tx_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_volume,
    
    -- 3. Average Monthly Volume for that wallet address across all active days in the month
    AVG(daily_volume) OVER (
        PARTITION BY blockchain, wallet_address, DATE_TRUNC('month', tx_date)
    ) AS avg_daily_volume_for_month
FROM daily_wallet_metrics
ORDER BY 
    blockchain, 
    wallet_address, 
    tx_date;
    
    
    
-- Create Materialized View  
CREATE MATERIALIZED VIEW mv_user_monthly_activity_summary AS
SELECT 
    u.id AS user_id,
    u.email,
    DATE_TRUNC('month', t.timestamp)::DATE AS activity_month,
    
    -- Transaction Volume & Counts
    COUNT(t.id) AS total_transactions,
    COALESCE(SUM(t.amount), 0.00) AS total_volume,
    COALESCE(SUM(t.fee), 0.00) AS total_fees_paid,
    
    -- Averages & Extremes
    ROUND(COALESCE(AVG(t.amount)::NUMERIC, 0.00), 2) AS avg_transaction_amount,
    COALESCE(MAX(t.amount), 0.00) AS max_transaction_amount,
    
    -- Status Breakdown
    COUNT(t.id) FILTER (WHERE t.status = 'CONFIRMED') AS confirmed_transactions,
    COUNT(t.id) FILTER (WHERE t.status = 'FAILED') AS failed_transactions,
    COUNT(t.id) FILTER (WHERE t.status = 'PENDING') AS pending_transactions,
    
    -- Confirmation Rate (%) with zero-division safety
    ROUND(
        (COUNT(t.id) FILTER (WHERE t.status = 'CONFIRMED')::NUMERIC / NULLIF(COUNT(t.id), 0)) * 100, 
        2
    ) AS confirmation_rate,
    
    -- Wallet Diversity & Timestamps
    COUNT(DISTINCT t.sender_wallet) AS active_wallets_used,
    MAX(t.timestamp) AS last_activity_timestamp

FROM users u
JOIN transactions t ON u.id = t.user_id
GROUP BY 
    u.id, 
    u.email, 
    DATE_TRUNC('month', t.timestamp);


SELECT * 
FROM mv_user_monthly_activity_summary

	
	
	
	
