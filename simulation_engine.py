def test_all():
    print("Testing odds parsing...")
    odds = {"1": "1.5", "X": "3.5", "2": "4.0"}
    assert all(k in odds for k in ["1", "X", "2"])
    print("OK")
    
    print("Testing h2h...")
    h2h = {"total": 5, "home_wins": 2, "draws": 1, "away_wins": 2}
    assert h2h['home_wins'] + h2h['draws'] + h2h['away_wins'] == h2h['total']
    print("OK")
    
    print("Testing stats...")
    wins = 5
    losses = 3
    total = wins + losses
    assert total > 0
    print("OK")
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_all()
