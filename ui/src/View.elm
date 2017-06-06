module View exposing (view)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Kinto
import Snippet exposing (snippets)
import Types exposing (..)
import Filesize


view : Model -> Html Msg
view model =
    div [ class "container" ]
        [ headerView model
        , case model.route of
            DocsView ->
                docsView model

            _ ->
                mainView model
        ]


mainView : Model -> Html Msg
mainView { loading, error, buildsPager, filters, filterValues } =
    div [ class "row" ]
        [ div [ class "col-sm-9" ]
            (if loading then
                [ spinner ]
             else
                [ errorView error
                , numBuilds buildsPager
                , div [] <| List.map recordView buildsPager.objects
                , nextPageBtn (List.length buildsPager.objects) buildsPager.total
                ]
            )
        , div [ class "col-sm-3" ]
            [ div [ class "panel panel-default" ]
                [ div [ class "panel-heading" ] [ strong [] [ text "Filters" ] ]
                , Html.form [ class "panel-body", onSubmit <| SubmitFilters ]
                    [ buildIdSearchForm filters.buildId
                    , filterSelector filterValues.productList "Products" filters.product (UpdateFilter << NewProductFilter)
                    , filterSelector filterValues.versionList "Versions" filters.version (UpdateFilter << NewVersionFilter)
                    , filterSelector filterValues.platformList "Platforms" filters.platform (UpdateFilter << NewPlatformFilter)
                    , filterSelector filterValues.channelList "Channels" filters.channel (UpdateFilter << NewChannelFilter)
                    , filterSelector filterValues.localeList "Locales" filters.locale (UpdateFilter << NewLocaleFilter)
                    , div [ class "btn-group btn-group-justified" ]
                        [ div [ class "btn-group" ]
                            [ button
                                [ class "btn btn-default", type_ "button", onClick (UpdateFilter ClearAll) ]
                                [ text "Reset" ]
                            ]
                        , div [ class "btn-group" ]
                            [ button
                                [ class "btn btn-default btn-primary", type_ "submit" ]
                                [ text "Search" ]
                            ]
                        ]
                    ]
                ]
            ]
        ]


snippetView : Snippet -> Html Msg
snippetView { title, description, snippets } =
    div [ class "panel panel-default" ]
        [ div [ class "panel-heading" ] [ text title ]
        , div [ class "panel-body" ]
            [ p [] [ text description ]
            , h4 [] [ text "cURL" ]
            , pre [] [ text snippets.curl ]
            , h4 [] [ text "JavaScript" ]
            , pre [] [ text snippets.js ]
            , h4 [] [ text "Python" ]
            , pre [] [ text snippets.python ]
            ]
        ]


docsView : Model -> Html Msg
docsView model =
    div []
        [ h2 [] [ text "About this project" ]
        , p []
            [ text "The BuildHub API is powered by "
            , a [ href "https://www.kinto-storage.org/" ] [ text "Kinto" ]
            , text "."
            ]
        , h2 [] [ text "Snippets" ]
        , p [] [ text "Here are a few useful snippets to browse or query the API, leveraging different Kinto clients." ]
        , div [] <| List.map snippetView snippets
        , h3 [] [ text "More information" ]
        , ul []
            [ li [] [ a [ href "http://kinto.readthedocs.io/en/stable/api/1.x/filtering.html" ] [ text "Filtering docs" ] ]
            , li [] [ a [ href "http://kinto.readthedocs.io/en/stable/api/1.x/" ] [ text "Full API reference" ] ]
            , li [] [ a [ href "https://github.com/Kinto/kinto-http.js" ] [ text "kinto-http.js (JavaScript)" ] ]
            , li [] [ a [ href "https://github.com/Kinto/kinto-http.py" ] [ text "kinto-http.py (Python)" ] ]
            , li [] [ a [ href "https://github.com/Kinto/kinto-http.rs" ] [ text "kinto-http.rs (Rust)" ] ]
            , li [] [ a [ href "https://github.com/Kinto/elm-kinto" ] [ text "elm-kinto (Elm)" ] ]
            , li [] [ a [ href "https://github.com/Kinto" ] [ text "Github organization" ] ]
            , li [] [ a [ href "https://github.com/Kinto/kinto" ] [ text "Kinto Server" ] ]
            ]
        , h3 [] [ text "Interested? Come talk to us!" ]
        , ul []
            [ li [] [ text "storage-team@mozilla.com" ]
            , li [] [ text "irc.freenode.net#kinto" ]
            ]
        ]


headerView : Model -> Html Msg
headerView model =
    nav
        [ class "navbar navbar-default" ]
        [ div
            [ class "container-fluid" ]
            [ div
                [ class "navbar-header" ]
                [ a [ class "navbar-brand", href "#" ] [ text "BuildHub" ] ]
            , div
                [ class "collapse navbar-collapse" ]
                [ ul
                    [ class "nav navbar-nav navbar-right" ]
                    [ li [] [ a [ href "#/builds" ] [ text "Builds" ] ]
                    , li []
                        [ a [ href "#/docs" ]
                            [ i [ class "glyphicon glyphicon-question-sign" ] []
                            , text " Docs"
                            ]
                        ]
                    ]
                ]
            ]
        ]


errorView : Maybe Kinto.Error -> Html Msg
errorView err =
    case err of
        Just err ->
            div [ class "panel panel-warning" ]
                [ div [ class "panel-heading" ]
                    [ h3 [ class "panel-title" ]
                        [ text "An error occured while fetching builds"
                        , button [ type_ "button", class "close", onClick DismissError ]
                            [ span [ class "glyphicon glyphicon-remove" ] []
                            ]
                        ]
                    ]
                , div [ class "panel-body" ]
                    [ text <| toString err ]
                ]

        _ ->
            div [] []


numBuilds : Kinto.Pager BuildRecord -> Html Msg
numBuilds pager =
    let
        nbBuilds =
            List.length pager.objects
    in
        p [ class "well" ] <|
            [ text <|
                (toString nbBuilds)
                    ++ " build"
                    ++ (if nbBuilds == 1 then
                            ""
                        else
                            "s"
                       )
                    ++ " displayed ("
                    ++ toString pager.total
                    ++ " total)."
            ]


buildIdSearchForm : String -> Html Msg
buildIdSearchForm buildId =
    div [ class "form-group" ]
        [ label [] [ text "Build id" ]
        , input
            [ type_ "text"
            , class "form-control"
            , placeholder "Eg. 201705011233"
            , value buildId
            , onInput <| UpdateFilter << NewBuildIdSearch
            ]
            []
        ]


filterSelector : List String -> String -> String -> (String -> Msg) -> Html Msg
filterSelector filters filterTitle selectedFilter updateHandler =
    let
        optionView value_ =
            option [ value value_, selected (value_ == selectedFilter) ] [ text value_ ]
    in
        div [ class "form-group", style [ ( "display", "block" ) ] ]
            [ label [] [ text filterTitle ]
            , select
                [ class "form-control"
                , onInput updateHandler
                , value selectedFilter
                ]
                (List.map optionView ("all" :: filters))
            ]


recordView : BuildRecord -> Html Msg
recordView record =
    div
        [ class "panel panel-default", Html.Attributes.id record.id ]
        [ div [ class "panel-heading" ]
            [ div [ class "row" ]
                [ strong [ class "col-sm-4" ]
                    [ a [ href <| "./#" ++ record.id ]
                        [ text <|
                            record.source.product
                                ++ " "
                                ++ record.target.version
                        ]
                    ]
                , small [ class "col-sm-4 text-center" ]
                    [ case record.build of
                        Just { date } ->
                            text date

                        Nothing ->
                            text ""
                    ]
                , em [ class "col-sm-4 text-right" ]
                    [ case record.build of
                        Just { id } ->
                            text id

                        Nothing ->
                            text ""
                    ]
                ]
            ]
        , div [ class "panel-body" ]
            [ viewSourceDetails record.source
            , viewTargetDetails record.target
            , viewDownloadDetails record.download
            , viewBuildDetails record.build
            , viewSystemAddonsDetails record.systemAddons
            ]
        ]


viewBuildDetails : Maybe Build -> Html Msg
viewBuildDetails build =
    case build of
        Just build ->
            div []
                [ h4 [] [ text "Build" ]
                , table [ class "table table-stripped table-condensed" ]
                    [ thead []
                        [ tr []
                            [ th [] [ text "Id" ]
                            , th [] [ text "Date" ]
                            ]
                        ]
                    , tbody []
                        [ tr []
                            [ td [] [ text build.id ]
                            , td [] [ text build.date ]
                            ]
                        ]
                    ]
                ]

        Nothing ->
            text ""


viewDownloadDetails : Download -> Html Msg
viewDownloadDetails download =
    let
        filename =
            String.split "/" download.url
                |> List.reverse
                |> List.head
                |> Maybe.withDefault ""
    in
        div []
            [ h4 [] [ text "Download" ]
            , table [ class "table table-stripped table-condensed" ]
                [ thead []
                    [ tr []
                        [ th [] [ text "URL" ]
                        , th [] [ text "Mimetype" ]
                        , th [] [ text "Size" ]
                        ]
                    ]
                , tbody []
                    [ tr []
                        [ td [] [ a [ href download.url ] [ text filename ] ]
                        , td [] [ text <| download.mimetype ]
                        , td [] [ text <| Filesize.formatBase2 download.size ]
                        ]
                    ]
                ]
            ]


viewSourceDetails : Source -> Html Msg
viewSourceDetails source =
    let
        revisionUrl =
            case source.revision of
                Just revision ->
                    case source.repository of
                        Just url ->
                            a [ href <| url ++ revision ] [ text revision ]

                        Nothing ->
                            text "If you see this, please file a bug. Revision not linked to a repository."

                Nothing ->
                    text ""
    in
        table [ class "table table-stripped table-condensed" ]
            [ thead []
                [ tr []
                    [ th [] [ text "Product" ]
                    , th [] [ text "Tree" ]
                    , th [] [ text "Revision" ]
                    ]
                ]
            , tbody []
                [ tr []
                    [ td [] [ text source.product ]
                    , td [] [ text <| Maybe.withDefault "unknown" source.tree ]
                    , td [] [ revisionUrl ]
                    ]
                ]
            ]


viewSystemAddonsDetails : List SystemAddon -> Html Msg
viewSystemAddonsDetails systemAddons =
    case systemAddons of
        [] ->
            text ""

        _ ->
            div []
                [ h4 [] [ text "System Addons" ]
                , table [ class "table table-stripped table-condensed" ]
                    [ thead []
                        [ tr []
                            [ th [] [ text "Id" ]
                            , th [] [ text "Builtin version" ]
                            , th [] [ text "Updated version" ]
                            ]
                        ]
                    , tbody []
                        (systemAddons
                            |> List.map
                                (\systemAddon ->
                                    tr []
                                        [ td [] [ text systemAddon.id ]
                                        , td [] [ text systemAddon.builtin ]
                                        , td [] [ text systemAddon.updated ]
                                        ]
                                )
                        )
                    ]
                ]


viewTargetDetails : Target -> Html Msg
viewTargetDetails target =
    div []
        [ h4 [] [ text "Target" ]
        , table
            [ class "table table-stripped table-condensed" ]
            [ thead []
                [ tr []
                    [ th [] [ text "Version" ]
                    , th [] [ text "Platform" ]
                    , th [] [ text "Channel" ]
                    , th [] [ text "Locale" ]
                    ]
                ]
            , tbody []
                [ tr []
                    [ td [] [ text target.version ]
                    , td [] [ text target.platform ]
                    , td [] [ text target.channel ]
                    , td [] [ text target.locale ]
                    ]
                ]
            ]
        ]


spinner : Html Msg
spinner =
    div [ class "loader" ] []


nextPageBtn : Int -> Int -> Html Msg
nextPageBtn displayed total =
    if displayed < total then
        button
            [ class "btn btn-default"
            , style [ ( "width", "100%" ) ]
            , onClick LoadNextPage
            ]
            [ text <|
                "Load "
                    ++ (toString pageSize)
                    ++ " more ("
                    ++ (toString <| total - displayed)
                    ++ " left)"
            ]
    else
        div [] []