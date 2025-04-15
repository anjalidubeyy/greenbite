import React from "react";
import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import "../styles/Home.css";

// Import all stickers
import Bean from "../assets/bean.png";
import Burger from "../assets/burger.png";
import Can from "../assets/can.png";
import Candy from "../assets/candy.png";
import Candy2 from "../assets/candy_2.png";
import Croissant from "../assets/croissant.png";
import Cupcake from "../assets/cupcake.png";
import CupcakeL from "../assets/cupcake_1.png";
import EggBacon from "../assets/egg-and-bacon.png";
import FriedEgg from "../assets/fried-egg.png";
import Fruit from "../assets/fruit.png";
import IceCream from "../assets/ice-cream.png";
import JapanFood from "../assets/japan-food.png";
import Noodle from "../assets/noodle.png";
import Pancake from "../assets/pancake.png";
import Pancake2 from "../assets/pancake_2.png";
import Pizza from "../assets/pizza.png";
import Tacos from "../assets/tacos.png";

const stickers = [
  Bean, Burger, Can, Candy, Candy2, Croissant, Cupcake, CupcakeL,
  EggBacon, FriedEgg, Fruit, IceCream, JapanFood, Noodle, 
  Pancake, Pancake2, Pizza, Tacos
];

const Stickers = () => {
  return (
    <div className="sticker-grid">
      {stickers.map((src, i) => (
        <img key={i} src={src} alt="" className="sticker" />
      ))}
    </div>
  );
};

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <Stickers />
      <h1>GreenBite</h1>
      <p className="tagline">Discover Deliciousness</p>
      <p className="sub-tagline">Know Your Food, Know Your Life</p>
      <div className="search-bar-container">
        <SearchBar />
        <button 
          className="compare-button"
          onClick={() => navigate('/compare')}
        >
          Compare Dishes
        </button>
      </div>
      <footer>
        <p>Made with ❤️ by Anjali Dubey</p>
      </footer>
    </div>
  );
}

export default Home;
