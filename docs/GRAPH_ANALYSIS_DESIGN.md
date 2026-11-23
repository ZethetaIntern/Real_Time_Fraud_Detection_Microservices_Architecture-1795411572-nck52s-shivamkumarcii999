# Graph-Based Fraud Detection & Relationship Analysis Design

Organized fraud rings, synthetic identity syndicates, and money laundering networks evade isolated rule and machine learning checks by distributing illicit transactions across hundreds of superficially distinct accounts. ShieldPay's **`graph-analysis-service`** utilizes **Neo4j Enterprise** to uncover these complex multi-entity topologies in real time.

```mermaid
graph TD
    subgraph FraudRingExample["Coordinated Synthetic Identity Ring Topology"]
        CARD1((Card A\nSynthetic))
        CARD2((Card B\nSynthetic))
        CARD3((Card C\nSynthetic))
        DEV1[Device Fingerprint\n#8841-A9]
        IP1[IP Subnet\n103.21.x.x (Proxy)]
        PHONE1[Shared Phone\n+91 98200xxxxx]
        ADDR1[Shared Address\nFlat 402, Highrise B]
        MERCH1{Merchant M\nElectronics}

        CARD1 -->|SHARED_DEVICE| DEV1
        CARD2 -->|SHARED_DEVICE| DEV1
        CARD3 -->|SHARED_DEVICE| DEV1

        CARD1 -->|USED_IP| IP1
        CARD2 -->|USED_IP| IP1
        CARD3 -->|USED_IP| IP1

        CARD1 -->|REGISTERED_PHONE| PHONE1
        CARD2 -->|REGISTERED_PHONE| PHONE1

        CARD1 -->|SHARED_ADDRESS| ADDR1
        CARD3 -->|SHARED_ADDRESS| ADDR1

        CARD1 -->|TRANSACTED_WITH| MERCH1
        CARD2 -->|TRANSACTED_WITH| MERCH1
        CARD3 -->|TRANSACTED_WITH| MERCH1
    end
```

---

## 1. Property Graph Schema Specification

### Node Labels & Properties
1. `(:Card)`: `card_hash` (Primary Key), `bin`, `issuer`, `product_type`, `created_at`, `status`
2. `(:Account)`: `account_id` (Primary Key), `customer_id`, `account_type`, `opened_at`, `risk_tier`
3. `(:Customer)`: `customer_hash` (Primary Key), `kyc_status`, `risk_tier`, `created_at`
4. `(:Device)`: `device_fingerprint` (Primary Key), `os`, `browser`, `first_seen`, `is_rooted`
5. `(:IPAddress)`: `ip_hash` (Primary Key), `country`, `city`, `asn`, `is_vpn`, `is_proxy`, `is_tor`
6. `(:PhoneNumber)`: `phone_hash` (Primary Key), `carrier`, `country_code`, `is_prepaid`
7. `(:Email)`: `email_hash` (Primary Key), `domain`, `is_disposable`
8. `(:PhysicalAddress)`: `address_hash` (Primary Key), `city`, `state`, `postal_code`, `country`
9. `(:Merchant)`: `merchant_id` (Primary Key), `mcc`, `merchant_name`, `risk_category`

### Relationship Types & Edge Properties
1. `[:TRANSACTED_WITH]`: `timestamp`, `amount`, `channel`, `currency`, `tx_id`
2. `[:SHARED_DEVICE]`: `first_shared_at`, `last_shared_at`, `tx_count`
3. `[:SHARED_ADDRESS]`: `relationship_type`, `verified_date`
4. `[:SAME_BENEFICIARY]`: `transfer_count`, `cumulative_amount`
5. `[:LINKED_ACCOUNT]`: `link_type`, `linked_at`
6. `[:USED_IP]`: `timestamp`, `session_duration`
7. `[:REGISTERED_PHONE]`: `registration_date`
8. `[:REGISTERED_EMAIL]`: `registration_date`

---

## 2. Five Production Cypher Query Patterns

### Query 1: Louvain Community Ring Detection (Detecting Dense Infrastructure Sharing)
Identifies densely interconnected clusters of cards sharing devices, phone numbers, and physical addresses:
```cypher
MATCH (c:Card {card_hash: $target_card_hash})
MATCH path = (c)-[:SHARED_DEVICE|REGISTERED_PHONE|SHARED_ADDRESS*1..3]-(other:Card)
WHERE other.card_hash <> $target_card_hash
WITH other, count(path) AS shared_links
WHERE shared_links >= 2
RETURN other.card_hash AS connected_card, 
       shared_links, 
       labels(other) AS labels
ORDER BY shared_links DESC
LIMIT 20;
```

### Query 2: PageRank Centrality (Flagging Shared Fraud Infrastructure Hubs)
Finds devices or IPs acting as abnormally central infrastructure nodes connecting multiple unrelated card accounts:
```cypher
MATCH (d:Device)
WHERE d.device_fingerprint = $target_device_fp
MATCH (d)<-[:SHARED_DEVICE]-(c:Card)
WITH d, count(DISTINCT c) AS linked_cards
WHERE linked_cards > 5
RETURN d.device_fingerprint AS infrastructure_id, 
       linked_cards,
       "CRITICAL_INFRASTRUCTURE_HUB" AS suspicion_reason;
```

### Query 3: Shortest Path to Confirmed Fraud Node
Measures topological distance (hops) between the transaction card and any confirmed fraudulent entity:
```cypher
MATCH (source:Card {card_hash: $target_card_hash}), 
      (fraud:Card {status: 'CONFIRMED_FRAUD'})
MATCH p = shortestPath((source)-[*..4]-(fraud))
RETURN length(p) AS degree_of_separation, 
       [n IN nodes(p) | coalesce(n.card_hash, n.device_fingerprint, n.phone_hash)] AS entities_in_path
ORDER BY degree_of_separation ASC
LIMIT 1;
```

### Query 4: Temporal Rapid Account Farming (Velocity Graph Growth)
Detects a device or IP address generating connections to more than 10 new card accounts in the last 7 days:
```cypher
MATCH (d:Device {device_fingerprint: $device_fp})<-[r:SHARED_DEVICE]-(c:Card)
WHERE r.first_shared_at >= (datetime() - duration({days: 7}))
WITH d, count(DISTINCT c) AS new_account_count
WHERE new_account_count > 10
RETURN d.device_fingerprint AS suspicious_device, 
       new_account_count, 
       "ACCOUNT_FARMING_SYNDICATE" AS threat_type;
```

### Query 5: Subgraph Topology Matching (E-Commerce Triangulation Fraud)
Matches the classic 3-way triangulation fraud loop (Card A -> Merchant M -> Shipping Address X <- Merchant N <- Card B sharing device D):
```cypher
MATCH (c1:Card {card_hash: $target_card_hash})-[:TRANSACTED_WITH]->(m1:Merchant)
MATCH (c1)-[:SHARED_ADDRESS]->(a:PhysicalAddress)
MATCH (c2:Card)-[:SHARED_ADDRESS]->(a)
MATCH (c1)-[:SHARED_DEVICE]->(d:Device)<-[:SHARED_DEVICE]-(c2:Card)
WHERE c1 <> c2
RETURN c1.card_hash AS target_card, 
       c2.card_hash AS accomplice_card, 
       a.address_hash AS shared_drop_address, 
       d.device_fingerprint AS shared_hardware
LIMIT 5;
```

---

## 3. Graph Synchronization, Indexing & Pruning Strategy

1. **Dual Update Strategy**:
   - **Real-Time Synchronous Check (<40ms)**: Evaluates read queries against Neo4j read replicas.
   - **Asynchronous Graph Mutation (<2 sec lag)**: Graph updates are consumed from Kafka `fraud.graph.updates` by a dedicated cluster of graph worker pods using batch Cypher `UNWIND` statements, insulating transaction processing latency from write lock overhead.
2. **Indexing Architecture**:
   - `CREATE CONSTRAINT FOR (c:Card) REQUIRE c.card_hash IS UNIQUE;`
   - `CREATE CONSTRAINT FOR (d:Device) REQUIRE d.device_fingerprint IS UNIQUE;`
   - `CREATE INDEX FOR (i:IPAddress) ON (i.ip_hash);`
   - `CREATE FULLTEXT INDEX merchantNameIndex FOR (m:Merchant) ON EACH [m.merchant_name];`
3. **Automated Pruning Strategy**:
   - Relationships older than 180 days are detached and deleted nightly by a Kubernetes CronJob (`MATCH ()-[r:TRANSACTED_WITH]->() WHERE r.timestamp < (datetime() - duration({days: 180})) DELETE r;`). Pruned records are archived to Parquet files in cold S3 storage.
