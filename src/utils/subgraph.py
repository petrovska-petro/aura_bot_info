# endpoints
BALANCER_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2"
SNAPSHOT_SUBGRAPH = "https://hub.snapshot.org/graphql?"

# pool ids ref
POOL_ID_BADGER = "0xb460daa847c45f1c4a41cb05bfb3b51c92e41b36000200000000000000000194"
POOL_ID_GRAVIAURA = "0x0578292cb20a443ba1cde459c985ce14ca2bdee5000100000000000000000269"
POOL_ID_DIGG = "0x8eb6c82c3081bbbd45dcac5afa631aac53478b7c000100000000000000000270"
POOL_ID_AURABAL_GRAVIAURA = (
    "0x0578292cb20a443ba1cde459c985ce14ca2bdee5000100000000000000000269"
)

# proposal bribe target
BRIBE_TARGET = "80/20 BADGER/WBTC"

# queries
TVL_QUERY = """
        query($pool_id: String) {
          pool(id: $pool_id) {
            totalLiquidity
          }
        }
        """

PROPOSAL_INFO_QUERY = """
        query($proposal_id: String) {
          proposal(id: $proposal_id) {
            scores_total
            snapshot
            choices
            scores
          }
        }
        """

VOTES_FROM_DELEGATE = """
        query($proposal_id: String, $voter_addr: String) {
          votes(
            where: {
              proposal: $proposal_id
              voter: $voter_addr
            }
          ) {
            choice
            vp
          }
        }
        """
