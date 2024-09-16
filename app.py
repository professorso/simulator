# app.py

import random
import streamlit as st
import matplotlib.pyplot as plt

# Define the Market Maker class
class MarketMaker:
    def __init__(self, initial_price=100, inventory=0, k=0.1, inventory_risk=0.05):
        self.price = initial_price
        self.inventory = inventory
        self.k = k  # Price impact factor
        self.inventory_risk = inventory_risk  # Inventory risk factor
        self.price_history = [initial_price]
        self.inventory_history = [inventory]
        self.profit_loss = 0
        self.pnl_history = [0]
        
    def adjust_price(self, order_size):
        # Price adjustment due to order size
        order_impact = self.k * order_size
        # Price adjustment due to inventory risk
        inventory_impact = self.inventory_risk * self.inventory
        # Total price adjustment
        price_adjustment = order_impact + inventory_impact
        # Update the price
        self.price += price_adjustment
        
    def execute_order(self, order_size):
        prev_price = self.price
        self.adjust_price(order_size)
        transaction_price = self.price
        self.inventory -= order_size
        # Update profit/loss
        self.profit_loss += -order_size * (transaction_price - prev_price)
        # Record history
        self.price_history.append(self.price)
        self.inventory_history.append(self.inventory)
        self.pnl_history.append(self.profit_loss)

# Define the Trader class
class Trader:
    def __init__(self, trader_id, strategy='random'):
        self.trader_id = trader_id
        self.strategy = strategy
        self.order_history = []
        self.trade_price_history = []
        self.inventory = 0
        
    def decide_order(self):
        if self.strategy == 'buy':
            order_size = random.randint(1, 10)
        elif self.strategy == 'sell':
            order_size = -random.randint(1, 10)
        elif self.strategy == 'random':
            order_size = random.randint(-10, 10)
        else:
            order_size = 0
        self.order_history.append(order_size)
        return order_size
        
    def record_trade(self, order_size, price):
        self.trade_price_history.append(price)
        self.inventory += order_size

# Define the Market class
class Market:
    def __init__(self, market_maker, traders):
        self.market_maker = market_maker
        self.traders = traders
        self.time_steps = 0
        
    def simulate_step(self):
        self.time_steps += 1
        for trader in self.traders:
            order_size = trader.decide_order()
            self.market_maker.execute_order(order_size)
            trader.record_trade(order_size, self.market_maker.price)

# Streamlit app code
def main():
    st.title("Interactive Market Maker Simulator")

    # Introduction text
    st.markdown("""
    Welcome to the **Interactive Market Maker Simulator**! This tool is designed to help you understand the concepts of **price impact**, **liquidity provision**, and **inventory risk** in financial markets.

    In this simulation, you can adjust parameters to see how a market maker interacts with traders, adjusts prices, and manages inventory risk.
    """)

    st.sidebar.header("Simulation Parameters")

    # User inputs for simulation parameters
    num_traders = st.sidebar.slider("Number of Traders", min_value=1, max_value=20, value=5)
    simulation_steps = st.sidebar.number_input("Simulation Steps per Run", min_value=1, max_value=500, value=50)
    initial_price = st.sidebar.number_input("Initial Market Price", min_value=1.0, max_value=1000.0, value=100.0)
    k = st.sidebar.slider("Price Impact Factor (k)", min_value=0.0, max_value=1.0, value=0.1, help="Controls how much the price adjusts based on order size.")
    inventory_risk = st.sidebar.slider("Inventory Risk Factor", min_value=0.0, max_value=0.5, value=0.05, help="Controls how much the price adjusts based on the market maker's inventory.")

    st.sidebar.header("Trader Strategies")
    trader_strategies = []
    for i in range(num_traders):
        strategy = st.sidebar.selectbox(f"Trader {i+1} Strategy", ('buy', 'sell', 'random'), index=2, key=f'strategy_{i}')
        trader_strategies.append(strategy)

    # Initialize market maker and traders
    market_maker = MarketMaker(initial_price=initial_price, k=k, inventory_risk=inventory_risk)
    traders = [Trader(trader_id=i+1, strategy=trader_strategies[i]) for i in range(num_traders)]
    market = Market(market_maker, traders)

    if st.button("Run Simulation"):
        for _ in range(simulation_steps):
            market.simulate_step()
        # Plotting the results
        st.subheader("Simulation Results")

        # Price History Plot
        st.markdown("### Market Price Over Time")
        st.line_chart(market_maker.price_history)

        # Inventory and Profit/Loss Plots
        st.markdown("### Market Maker's Inventory and Profit/Loss Over Time")
        fig, axs = plt.subplots(1, 2, figsize=(14, 5))

        # Inventory Plot
        axs[0].plot(market_maker.inventory_history, label='Inventory Level', color='orange')
        axs[0].set_title('Market Maker Inventory Level Over Time')
        axs[0].set_xlabel('Time Steps')
        axs[0].set_ylabel('Inventory Level (Number of Shares)')
        axs[0].legend()
        axs[0].grid(True)

        # Profit/Loss Plot
        axs[1].plot(market_maker.pnl_history, label='Cumulative Profit/Loss', color='green')
        axs[1].set_title('Market Maker Cumulative Profit/Loss Over Time')
        axs[1].set_xlabel('Time Steps')
        axs[1].set_ylabel('Profit/Loss (Currency Units)')
        axs[1].legend()
        axs[1].grid(True)

        st.pyplot(fig)

        # Optionally, display trader inventories
        show_trader_info = st.checkbox("Show Traders' Inventory Over Time")
        if show_trader_info:
            st.markdown("### Traders' Inventory Levels Over Time")
            fig_traders, ax_traders = plt.subplots(figsize=(10, 6))
            for trader in traders:
                trader_inventory = [sum(trader.order_history[:i+1]) for i in range(len(trader.order_history))]
                ax_traders.plot(trader_inventory, label=f'Trader {trader.trader_id} ({trader.strategy})')
            ax_traders.set_title("Traders' Inventory Levels Over Time")
            ax_traders.set_xlabel('Time Steps')
            ax_traders.set_ylabel('Inventory Level (Number of Shares)')
            ax_traders.legend()
            ax_traders.grid(True)
            st.pyplot(fig_traders)

        # Add explanations for the results
        st.markdown("""
        **Interpretation of Results:**

        - **Market Price Over Time**: Shows how the market price fluctuates in response to traders' orders and the market maker's price adjustments.
        - **Market Maker Inventory Level**: Illustrates how the market maker's inventory changes over time, reflecting the imbalance between buy and sell orders.
        - **Market Maker Profit/Loss**: Displays the cumulative profit or loss for the market maker, highlighting the financial impact of providing liquidity.
        - **Traders' Inventory Levels**: (Optional) Shows how each trader's inventory changes over time based on their trading strategy.
        """)

    else:
        st.info("Adjust the simulation parameters and click **Run Simulation** to start.")

    # Add a footer with more information
    st.markdown("""
    ---
    **About this Simulator**

    This simulator models a simplified financial market to illustrate the concepts of **price impact**, **liquidity provision**, and **inventory risk** faced by market makers. It demonstrates how market makers adjust prices in response to order flow and manage their inventory levels to mitigate risk.

    **How to Use the Simulator in Class**

    - **Experiment with Parameters**: Encourage students to adjust parameters like the number of traders, their strategies, the price impact factor, and the inventory risk factor to observe different market dynamics.
    - **Discuss the Results**: Use the generated plots to facilitate discussions about how market makers influence prices, manage risks, and how traders' behaviors impact the market.
    - **Scenario Analysis**: Pose hypothetical scenarios (e.g., what happens if all traders are buyers?) and have students predict and then test the outcomes using the simulator.
    """)

if __name__ == "__main__":
    main()
