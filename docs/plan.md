# ToagiHouse Character Memory System 実装計画

## 実装の全体方針

階層的記憶システムを既存のチャットアプリケーションに統合するため、以下の 4 つの主要コンポーネントに分けて開発を進めます：

1. **データアクセス層** : Supabase との連携とデータモデルの操作
2. **記憶管理エンジン** : 記憶の取得・保存・要約処理
3. **API レイヤー** : フロントエンドとバックエンドの連携
4. **ユーザーインターフェース** : キャラクター管理とチャット機能の拡張

## タスク分解

### Phase 1: データアクセス層 (4 日) ✅

#### 1.1 Supabase 接続設定 (1 日) ✅

- [x] 環境変数の確認（`SUPABASE_DB_PASSWORD`は設定済み）
- [x] Supabase 接続テスト
- [x] Supabase 接続設定ドキュメントの作成（`docs/devin.md`）

#### 1.2 データアクセス関数の実装 (2 日) ✅

- [x] キャラクター管理（CRUD 操作）
  - [x] キャラクター作成関数
  - [x] キャラクター取得関数
  - [x] キャラクター更新関数
  - [x] キャラクター削除関数
- [x] 記憶管理（CRUD 操作）
  - [x] 記憶追加関数
  - [x] 記憶検索・取得関数
  - [x] 記憶更新関数
  - [x] 記憶削除関数
- [x] セッション管理（CRUD 操作）
  - [x] セッション作成関数
  - [x] セッション取得関数
  - [x] セッション更新関数
  - [x] セッション終了関数

#### 1.3 追加マイグレーションと RLS 設定 (1 日) ✅

- [x] カスタムマイグレーションの作成（キャラクターの睡眠状態と記憶処理日時の追加）
- [x] RLS ポリシーの検証と調整
- [x] インデックス最適化

### Phase 2: 記憶管理エンジン (5 日) ✅

#### 2.1 記憶構造設計 (1 日) ✅

- [x] 記憶タイプごとのデータ構造を定義
- [x] 記憶間の関係性マッピング
- [x] 日付・時間管理方法の確立

#### 2.2 記憶生成プロセスの実装 (2 日) ✅

- [x] 生会話の daily_raw 記憶への変換
- [x] daily_summary の生成ロジック
- [x] 階層的要約（level_10, level_100, level_1000）の生成ロジック
- [x] LLM を使用した要約処理の実装

#### 2.3 記憶取得プロセスの実装 (1 日) ✅

- [x] セッションコンテキストに必要な記憶を選択するロジック
- [x] 時間的関連性に基づく記憶の重み付け
- [x] コンテキスト制限に合わせた記憶の選定ロジック

#### 2.4 記憶管理スケジュールの実装 (1 日) ✅

- [x] 要約処理のトリガー条件設定
- [x] バックグラウンド処理ワークフローの実装
- [x] エラー処理と再試行メカニズム

### Phase 3: API レイヤー (3 日) 🔄

#### 3.1 バックエンド API エンドポイント拡張 (1.5 日)

- [ ] キャラクター管理エンドポイント
  - [ ] キャラクター作成 API
  - [ ] キャラクター一覧 API
  - [ ] キャラクター詳細 API
  - [ ] キャラクター更新 API
  - [ ] キャラクター削除 API
- [ ] 記憶管理エンドポイント
  - [ ] 記憶検索・取得 API
  - [ ] 記憶階層表示 API
- [ ] セッション管理エンドポイント
  - [ ] セッション作成・終了 API
  - [ ] アクティブセッション取得 API

#### 3.2 チャットエンドポイント拡張 (1.5 日)

- [x] 基本的なチャット機能 API
- [x] 利用可能なモデル一覧 API
- [ ] キャラクターコンテキスト付きチャット API
- [ ] セッション管理との統合
- [ ] 記憶保存プロセスの統合
- [ ] 記憶生成トリガーの実装

### Phase 4: ユーザーインターフェース (5 日)

#### 4.1 キャラクター管理 UI (2 日)

- [ ] キャラクター一覧画面
- [ ] キャラクター作成・編集フォーム
- [ ] キャラクター設定画面

#### 4.2 チャットインターフェース拡張 (2 日)

- [x] 基本的なチャットインターフェース
- [x] モデル選択機能
- [x] ストリーミング/非ストリーミング切り替え
- [ ] キャラクター選択機能
- [ ] セッション情報表示
- [ ] 記憶情報の可視化コンポーネント

#### 4.3 記憶閲覧インターフェース (1 日)

- [ ] 階層別記憶閲覧 UI
- [ ] 時系列記憶検索機能
- [ ] 記憶視覚化（タイムライン等）

### Phase 5: 統合・テスト (3 日)

#### 5.1 コンポーネント統合 (1 日)

- [ ] 全レイヤーの接続確認
- [ ] エンドツーエンドワークフロー検証

#### 5.2 テストケース実装 (1 日)

- [x] CRUD 操作の単体テスト
- [x] 記憶エンジンの単体テスト
- [ ] API 統合テスト
- [ ] エンドツーエンドテスト

#### 5.3 デバッグと最適化 (1 日)

- [ ] パフォーマンス測定
- [ ] ボトルネック特定と最適化
- [ ] エラー処理の改善

## 現在の進捗状況

- **完了済み** :
- データアクセス層（Phase 1）: Supabase 接続、CRUD オペレーション、マイグレーション設計
- 記憶管理エンジン（Phase 2）: 記憶構造設計、記憶生成・取得・処理ロジック
- 基本的なチャット機能（Phase 3 の一部）: チャット API、モデル一覧取得
- 基本的な UI コンポーネント（Phase 4 の一部）: チャットインターフェース、モデル選択
- 一部のテスト実装（Phase 5 の一部）: CRUD 操作と記憶エンジンの単体テスト
- **現在のフォーカス** :
- API レイヤーの拡張（Phase 3）: キャラクター管理、記憶管理、セッション管理の API エンドポイント実装
- **次のステップ** :

1. キャラクター管理 API エンドポイントの実装
2. 記憶管理 API エンドポイントの実装
3. キャラクターと記憶を統合したチャット API の実装
4. フロントエンド UI の拡張

## 想定される課題と対策

1. **コンテキスト管理** :

- 課題: LLM のコンテキスト窓制限内に適切な記憶を収める
- 対策: 重要度に基づく記憶選択アルゴリズムの実装

1. **記憶の一貫性** :

- 課題: 異なる階層の記憶間で矛盾が生じる可能性
- 対策: 要約生成時の一貫性チェックと矛盾検出メカニズム

1. **パフォーマンス** :

- 課題: 記憶検索・生成の遅延がユーザー体験に影響
- 対策: キャッシング、非同期処理、バックグラウンド要約生成

1. **コスト管理** :

- 課題: LLM の頻繁な使用による API コストの増大
- 対策: バッチ処理、要約頻度の最適化、キャッシュ活用

1. **テスト環境の整備** :

- 課題: LLM を使用するテストが API キー認証に依存
- 対策: モックを使用したテスト環境の整備（実装済み）

## 次のマイルストーン（2 週間）

1. **Week 1** : API レイヤーの完成

- キャラクター管理 API の実装（2 日）
- 記憶管理 API の実装（2 日）
- チャット API との統合（1 日）

1. **Week 2** : フロントエンド UI の拡張と統合

- キャラクター管理 UI の実装（2 日）
- 拡張チャットインターフェースの実装（2 日）
- 統合テストとバグ修正（1 日）
